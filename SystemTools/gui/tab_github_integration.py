"""
GitHub Integration Tab for DPM Diagnostic Tool
Provides GitHub issue tracking and project management integration
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Optional, Dict, List
from pathlib import Path

from utils.logger import logger
from utils.config import config


class GitHubIntegrationTab(ttk.Frame):
    """GitHub Integration tab - manage issues and project tracking"""

    # GitHub API configuration
    GITHUB_API_BASE = "https://api.github.com"
    REPO_OWNER = "unmanned-systems-uk"
    REPO_NAME = "DPM-V2"

    # Issue states
    STATE_OPEN = "open"
    STATE_CLOSED = "closed"
    STATE_ALL = "all"

    def __init__(self, parent):
        super().__init__(parent)

        self.issues = []  # Cache of fetched issues
        self.current_issue = None  # Currently selected issue
        self.labels_cache = []  # Available labels

        # Variables
        self.state_var = tk.StringVar(value="open")
        self.label_filter_var = tk.StringVar(value="All")
        self.search_var = tk.StringVar()

        # GitHub token (optional, for authenticated requests)
        self.github_token = config.get('github', 'token', '')

        self._create_ui()
        self._load_initial_data()

        logger.debug("GitHub Integration tab initialized")

    def _create_ui(self):
        """Create UI elements"""
        # Create PanedWindow for resizable sections
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel: Issue list
        left_panel = ttk.Frame(paned)
        paned.add(left_panel, weight=1)
        self._create_issue_list_panel(left_panel)

        # Right panel: Issue details and actions
        right_panel = ttk.Frame(paned)
        paned.add(right_panel, weight=1)
        self._create_details_panel(right_panel)

    def _create_issue_list_panel(self, parent):
        """Create issue list panel"""
        # Top: Controls and filters
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # Repository info
        repo_label = ttk.Label(
            control_frame,
            text=f"Repository: {self.REPO_OWNER}/{self.REPO_NAME}",
            font=("TkDefaultFont", 10, "bold")
        )
        repo_label.pack(side=tk.TOP, anchor=tk.W, pady=(0, 5))

        # Filter controls
        filter_frame = ttk.Frame(control_frame)
        filter_frame.pack(fill=tk.X)

        # State filter
        ttk.Label(filter_frame, text="State:").pack(side=tk.LEFT, padx=2)
        state_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.state_var,
            values=["open", "closed", "all"],
            state="readonly",
            width=10
        )
        state_combo.pack(side=tk.LEFT, padx=2)
        state_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_issues())

        # Label filter
        ttk.Label(filter_frame, text="Label:").pack(side=tk.LEFT, padx=(10, 2))
        self.label_filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.label_filter_var,
            values=["All"],
            state="readonly",
            width=15
        )
        self.label_filter_combo.pack(side=tk.LEFT, padx=2)
        self.label_filter_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())

        # Refresh button
        ttk.Button(filter_frame, text="Refresh", command=self._refresh_issues, width=10).pack(
            side=tk.RIGHT, padx=2
        )

        # Search bar
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, padx=5, pady=2)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=2)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        search_entry.bind("<KeyRelease>", lambda e: self._apply_filters())

        # Issue list
        list_frame = ttk.LabelFrame(parent, text="Issues", padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # TreeView for issues
        columns = ("number", "title", "labels", "state")
        self.issue_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        # Define headings
        self.issue_tree.heading("number", text="#")
        self.issue_tree.heading("title", text="Title")
        self.issue_tree.heading("labels", text="Labels")
        self.issue_tree.heading("state", text="State")

        # Define column widths
        self.issue_tree.column("number", width=50)
        self.issue_tree.column("title", width=300)
        self.issue_tree.column("labels", width=150)
        self.issue_tree.column("state", width=70)

        # Configure tags for states
        self.issue_tree.tag_configure("open", foreground="#238636")
        self.issue_tree.tag_configure("closed", foreground="#8b949e")

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.issue_tree.yview)
        self.issue_tree.configure(yscrollcommand=scrollbar.set)

        self.issue_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind selection event
        self.issue_tree.bind("<<TreeviewSelect>>", self._on_issue_selected)

        # Statistics
        self.stats_label = ttk.Label(parent, text="Issues: 0 open, 0 closed")
        self.stats_label.pack(side=tk.BOTTOM, padx=5, pady=2)

    def _create_details_panel(self, parent):
        """Create issue details and actions panel"""
        # Notebook for different views
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: View Issue Details
        self.view_tab = ttk.Frame(notebook)
        notebook.add(self.view_tab, text="View Issue")
        self._create_view_issue_tab(self.view_tab)

        # Tab 2: Create New Issue
        self.create_tab = ttk.Frame(notebook)
        notebook.add(self.create_tab, text="Create Issue")
        self._create_new_issue_tab(self.create_tab)

        # Tab 3: Settings
        self.settings_tab = ttk.Frame(notebook)
        notebook.add(self.settings_tab, text="Settings")
        self._create_settings_tab(self.settings_tab)

    def _create_view_issue_tab(self, parent):
        """Create view issue details tab"""
        # Issue header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        self.issue_title_label = ttk.Label(
            header_frame,
            text="Select an issue to view details",
            font=("TkDefaultFont", 11, "bold"),
            wraplength=400
        )
        self.issue_title_label.pack(anchor=tk.W)

        self.issue_meta_label = ttk.Label(
            header_frame,
            text="",
            font=("TkDefaultFont", 9),
            foreground="#666666"
        )
        self.issue_meta_label.pack(anchor=tk.W, pady=(2, 0))

        # Issue body
        body_frame = ttk.LabelFrame(parent, text="Description", padding=5)
        body_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.issue_body_text = scrolledtext.ScrolledText(
            body_frame,
            wrap=tk.WORD,
            height=10,
            state=tk.DISABLED,
            font=("TkDefaultFont", 10)
        )
        self.issue_body_text.pack(fill=tk.BOTH, expand=True)

        # Comments section
        comments_frame = ttk.LabelFrame(parent, text="Comments", padding=5)
        comments_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.comments_text = scrolledtext.ScrolledText(
            comments_frame,
            wrap=tk.WORD,
            height=8,
            state=tk.DISABLED,
            font=("TkDefaultFont", 9)
        )
        self.comments_text.pack(fill=tk.BOTH, expand=True)

        # Action buttons
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(
            action_frame,
            text="Open in Browser",
            command=self._open_issue_in_browser
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            action_frame,
            text="Refresh",
            command=self._refresh_current_issue
        ).pack(side=tk.LEFT, padx=2)

        # Add comment section
        comment_frame = ttk.LabelFrame(parent, text="Add Comment", padding=5)
        comment_frame.pack(fill=tk.X, padx=10, pady=5)

        self.new_comment_text = scrolledtext.ScrolledText(
            comment_frame,
            wrap=tk.WORD,
            height=3,
            font=("TkDefaultFont", 9)
        )
        self.new_comment_text.pack(fill=tk.BOTH, expand=True)

        comment_buttons = ttk.Frame(comment_frame)
        comment_buttons.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(
            comment_buttons,
            text="Add Comment",
            command=self._add_comment
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            comment_buttons,
            text="Close Issue",
            command=self._close_issue
        ).pack(side=tk.RIGHT, padx=2)

        ttk.Button(
            comment_buttons,
            text="Reopen Issue",
            command=self._reopen_issue
        ).pack(side=tk.RIGHT, padx=2)

    def _create_new_issue_tab(self, parent):
        """Create new issue creation tab"""
        # Title
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(title_frame, text="Title:").pack(anchor=tk.W)
        self.new_issue_title = ttk.Entry(title_frame, font=("TkDefaultFont", 10))
        self.new_issue_title.pack(fill=tk.X, pady=(2, 0))

        # Body
        body_frame = ttk.LabelFrame(parent, text="Description", padding=5)
        body_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.new_issue_body = scrolledtext.ScrolledText(
            body_frame,
            wrap=tk.WORD,
            height=15,
            font=("TkDefaultFont", 10)
        )
        self.new_issue_body.pack(fill=tk.BOTH, expand=True)

        # Labels
        label_frame = ttk.Frame(parent)
        label_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(label_frame, text="Labels (comma-separated):").pack(anchor=tk.W)
        self.new_issue_labels = ttk.Entry(label_frame)
        self.new_issue_labels.pack(fill=tk.X, pady=(2, 0))

        # Common labels help text
        help_text = ttk.Label(
            label_frame,
            text="Common: air-side, ground-side, dev-tools, bug, enhancement, documentation",
            font=("TkDefaultFont", 8),
            foreground="#666666"
        )
        help_text.pack(anchor=tk.W, pady=(2, 0))

        # Assignee
        assignee_frame = ttk.Frame(parent)
        assignee_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(assignee_frame, text="Assignee (username):").pack(anchor=tk.W)
        self.new_issue_assignee = ttk.Entry(assignee_frame)
        self.new_issue_assignee.pack(fill=tk.X, pady=(2, 0))

        # Buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(
            button_frame,
            text="Create Issue",
            command=self._create_issue
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            button_frame,
            text="Clear Form",
            command=self._clear_new_issue_form
        ).pack(side=tk.LEFT, padx=2)

    def _create_settings_tab(self, parent):
        """Create settings tab for GitHub configuration"""
        settings_frame = ttk.Frame(parent)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # GitHub Token
        token_frame = ttk.LabelFrame(settings_frame, text="Authentication", padding=10)
        token_frame.pack(fill=tk.X, pady=5)

        ttk.Label(
            token_frame,
            text="GitHub Personal Access Token (optional):",
            font=("TkDefaultFont", 9)
        ).pack(anchor=tk.W)

        ttk.Label(
            token_frame,
            text="Provides higher rate limits and access to private repositories",
            font=("TkDefaultFont", 8),
            foreground="#666666"
        ).pack(anchor=tk.W, pady=(0, 5))

        self.token_entry = ttk.Entry(token_frame, show="*", width=50)
        self.token_entry.pack(fill=tk.X, pady=2)
        self.token_entry.insert(0, self.github_token)

        token_buttons = ttk.Frame(token_frame)
        token_buttons.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(
            token_buttons,
            text="Save Token",
            command=self._save_github_token
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            token_buttons,
            text="Clear Token",
            command=self._clear_github_token
        ).pack(side=tk.LEFT, padx=2)

        # Help text
        help_frame = ttk.LabelFrame(settings_frame, text="How to get a GitHub Token", padding=10)
        help_frame.pack(fill=tk.X, pady=10)

        help_text = """1. Go to GitHub Settings > Developer Settings > Personal Access Tokens > Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "DPM DevTools")
4. Select scopes: 'repo' (for private repos) or 'public_repo' (for public repos only)
5. Click "Generate token"
6. Copy the token and paste it above
7. Click "Save Token"

Without a token: 60 requests/hour limit (public API)
With a token: 5000 requests/hour + access to private repositories"""

        help_label = ttk.Label(
            help_frame,
            text=help_text.strip(),
            font=("TkDefaultFont", 8),
            justify=tk.LEFT
        )
        help_label.pack(anchor=tk.W)

        # API status
        status_frame = ttk.LabelFrame(settings_frame, text="API Status", padding=10)
        status_frame.pack(fill=tk.X, pady=5)

        self.api_status_label = ttk.Label(
            status_frame,
            text="Click 'Check Status' to view API rate limits",
            font=("TkDefaultFont", 9)
        )
        self.api_status_label.pack(anchor=tk.W)

        ttk.Button(
            status_frame,
            text="Check Status",
            command=self._check_api_status
        ).pack(anchor=tk.W, pady=(5, 0))

    def _load_initial_data(self):
        """Load initial data from GitHub"""
        # Load labels
        self._fetch_labels()

        # Load issues
        self._refresh_issues()

    def _make_github_request(
        self,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Make a request to GitHub API"""
        url = f"{self.GITHUB_API_BASE}/repos/{self.REPO_OWNER}/{self.REPO_NAME}{endpoint}"

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DPM-DevTools"
        }

        # Add authentication if token is available
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"

        try:
            if data:
                json_data = json.dumps(data).encode('utf-8')
                headers["Content-Type"] = "application/json"
                req = urllib.request.Request(url, data=json_data, headers=headers, method=method)
            else:
                req = urllib.request.Request(url, headers=headers, method=method)

            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))

        except urllib.error.HTTPError as e:
            error_msg = f"GitHub API error: {e.code} {e.reason}"
            try:
                error_data = json.loads(e.read().decode('utf-8'))
                if 'message' in error_data:
                    error_msg = f"{error_msg} - {error_data['message']}"
                # Add validation errors if present
                if 'errors' in error_data:
                    validation_errors = []
                    for err in error_data['errors']:
                        if isinstance(err, dict):
                            field = err.get('field', err.get('resource', 'unknown'))
                            code = err.get('code', 'error')
                            validation_errors.append(f"{field}: {code}")
                        else:
                            validation_errors.append(str(err))
                    if validation_errors:
                        error_msg += f"\nValidation errors: {', '.join(validation_errors)}"
            except:
                pass
            logger.error(error_msg)
            messagebox.showerror("GitHub API Error", error_msg)
            return None

        except urllib.error.URLError as e:
            error_msg = f"Network error: {e.reason}"
            logger.error(error_msg)
            messagebox.showerror("Network Error", error_msg)
            return None

        except Exception as e:
            error_msg = f"Error making GitHub request: {e}"
            logger.error(error_msg)
            messagebox.showerror("Error", error_msg)
            return None

    def _fetch_labels(self):
        """Fetch available labels from repository"""
        response = self._make_github_request("/labels")

        if response:
            self.labels_cache = [label['name'] for label in response]
            # Update label filter dropdown
            self.label_filter_combo['values'] = ["All"] + self.labels_cache
            logger.info(f"Loaded {len(self.labels_cache)} labels")

    def _refresh_issues(self):
        """Fetch and display issues from GitHub"""
        state = self.state_var.get()
        endpoint = f"/issues?state={state}&per_page=100"

        response = self._make_github_request(endpoint)

        if response:
            self.issues = response
            self._apply_filters()
            self._update_statistics()
            logger.info(f"Loaded {len(self.issues)} {state} issues")

    def _apply_filters(self):
        """Apply filters to issue list"""
        # Clear current items
        for item in self.issue_tree.get_children():
            self.issue_tree.delete(item)

        # Get filter values
        search_term = self.search_var.get().lower()
        label_filter = self.label_filter_var.get()

        # Filter and display issues
        for issue in self.issues:
            # Apply search filter
            if search_term:
                title = issue['title'].lower()
                body = issue.get('body', '').lower() if issue.get('body') else ''
                if search_term not in title and search_term not in body:
                    continue

            # Apply label filter
            if label_filter != "All":
                issue_labels = [label['name'] for label in issue.get('labels', [])]
                if label_filter not in issue_labels:
                    continue

            # Add to tree
            number = issue['number']
            title = issue['title']
            labels = ', '.join([label['name'] for label in issue.get('labels', [])])
            state = issue['state']

            tag = "open" if state == "open" else "closed"
            self.issue_tree.insert(
                "",
                tk.END,
                values=(number, title, labels, state),
                tags=(tag,)
            )

    def _update_statistics(self):
        """Update statistics label"""
        open_count = sum(1 for issue in self.issues if issue['state'] == 'open')
        closed_count = sum(1 for issue in self.issues if issue['state'] == 'closed')
        self.stats_label.config(text=f"Issues: {open_count} open, {closed_count} closed")

    def _on_issue_selected(self, event):
        """Handle issue selection"""
        selection = self.issue_tree.selection()
        if not selection:
            return

        # Get selected issue number
        item = self.issue_tree.item(selection[0])
        issue_number = item['values'][0]

        # Find issue in cache
        for issue in self.issues:
            if issue['number'] == issue_number:
                self.current_issue = issue
                self._display_issue_details(issue)
                break

    def _display_issue_details(self, issue: Dict):
        """Display issue details in the view tab"""
        # Update title
        self.issue_title_label.config(text=f"#{issue['number']}: {issue['title']}")

        # Update metadata
        created_at = datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00'))
        author = issue['user']['login']
        state = issue['state'].upper()
        meta_text = f"By {author} • {created_at.strftime('%Y-%m-%d %H:%M')} • {state}"
        self.issue_meta_label.config(text=meta_text)

        # Update body
        self.issue_body_text.config(state=tk.NORMAL)
        self.issue_body_text.delete(1.0, tk.END)
        body = issue.get('body', 'No description provided.')
        if body:
            self.issue_body_text.insert(1.0, body)
        self.issue_body_text.config(state=tk.DISABLED)

        # Fetch and display comments
        self._fetch_and_display_comments(issue['number'])

    def _fetch_and_display_comments(self, issue_number: int):
        """Fetch and display comments for an issue"""
        response = self._make_github_request(f"/issues/{issue_number}/comments")

        self.comments_text.config(state=tk.NORMAL)
        self.comments_text.delete(1.0, tk.END)

        if response:
            if len(response) == 0:
                self.comments_text.insert(1.0, "No comments yet.")
            else:
                for i, comment in enumerate(response):
                    author = comment['user']['login']
                    created_at = datetime.fromisoformat(comment['created_at'].replace('Z', '+00:00'))
                    body = comment['body']

                    comment_text = f"--- Comment by {author} on {created_at.strftime('%Y-%m-%d %H:%M')} ---\n"
                    comment_text += f"{body}\n\n"

                    self.comments_text.insert(tk.END, comment_text)

        self.comments_text.config(state=tk.DISABLED)

    def _refresh_current_issue(self):
        """Refresh the currently selected issue"""
        if not self.current_issue:
            messagebox.showinfo("No Issue Selected", "Please select an issue first.")
            return

        issue_number = self.current_issue['number']
        response = self._make_github_request(f"/issues/{issue_number}")

        if response:
            self.current_issue = response
            self._display_issue_details(response)

            # Update in cache
            for i, issue in enumerate(self.issues):
                if issue['number'] == issue_number:
                    self.issues[i] = response
                    break

            self._apply_filters()

    def _open_issue_in_browser(self):
        """Open current issue in web browser"""
        if not self.current_issue:
            messagebox.showinfo("No Issue Selected", "Please select an issue first.")
            return

        import webbrowser
        url = self.current_issue['html_url']
        webbrowser.open(url)

    def _add_comment(self):
        """Add a comment to the current issue"""
        if not self.current_issue:
            messagebox.showinfo("No Issue Selected", "Please select an issue first.")
            return

        comment_text = self.new_comment_text.get(1.0, tk.END).strip()

        if not comment_text:
            messagebox.showwarning("Empty Comment", "Please enter a comment.")
            return

        if not self.github_token:
            messagebox.showerror(
                "Authentication Required",
                "You need to set a GitHub token in Settings to add comments."
            )
            return

        # Post comment
        issue_number = self.current_issue['number']
        data = {"body": comment_text}

        response = self._make_github_request(
            f"/issues/{issue_number}/comments",
            method="POST",
            data=data
        )

        if response:
            messagebox.showinfo("Success", "Comment added successfully!")
            self.new_comment_text.delete(1.0, tk.END)
            self._refresh_current_issue()

    def _close_issue(self):
        """Close the current issue"""
        if not self.current_issue:
            messagebox.showinfo("No Issue Selected", "Please select an issue first.")
            return

        if not self.github_token:
            messagebox.showerror(
                "Authentication Required",
                "You need to set a GitHub token in Settings to close issues."
            )
            return

        if not messagebox.askyesno("Confirm", "Are you sure you want to close this issue?"):
            return

        issue_number = self.current_issue['number']
        data = {"state": "closed"}

        response = self._make_github_request(
            f"/issues/{issue_number}",
            method="PATCH",
            data=data
        )

        if response:
            messagebox.showinfo("Success", "Issue closed successfully!")
            self._refresh_issues()

    def _reopen_issue(self):
        """Reopen the current issue"""
        if not self.current_issue:
            messagebox.showinfo("No Issue Selected", "Please select an issue first.")
            return

        if not self.github_token:
            messagebox.showerror(
                "Authentication Required",
                "You need to set a GitHub token in Settings to reopen issues."
            )
            return

        issue_number = self.current_issue['number']
        data = {"state": "open"}

        response = self._make_github_request(
            f"/issues/{issue_number}",
            method="PATCH",
            data=data
        )

        if response:
            messagebox.showinfo("Success", "Issue reopened successfully!")
            self._refresh_issues()

    def _create_issue(self):
        """Create a new issue"""
        title = self.new_issue_title.get().strip()
        body = self.new_issue_body.get(1.0, tk.END).strip()
        labels_str = self.new_issue_labels.get().strip()
        assignee = self.new_issue_assignee.get().strip()

        if not title:
            messagebox.showwarning("Missing Title", "Please enter an issue title.")
            return

        if not self.github_token:
            messagebox.showerror(
                "Authentication Required",
                "You need to set a GitHub token in Settings to create issues."
            )
            return

        # Prepare data
        data = {
            "title": title,
            "body": body if body else ""
        }

        if labels_str:
            labels = [label.strip() for label in labels_str.split(',')]
            data["labels"] = labels

        if assignee:
            data["assignees"] = [assignee]

        # Create issue
        response = self._make_github_request("/issues", method="POST", data=data)

        if response:
            issue_number = response['number']
            messagebox.showinfo("Success", f"Issue #{issue_number} created successfully!")
            self._clear_new_issue_form()
            self._refresh_issues()

    def _clear_new_issue_form(self):
        """Clear the new issue form"""
        self.new_issue_title.delete(0, tk.END)
        self.new_issue_body.delete(1.0, tk.END)
        self.new_issue_labels.delete(0, tk.END)
        self.new_issue_assignee.delete(0, tk.END)

    def _save_github_token(self):
        """Save GitHub token to configuration"""
        token = self.token_entry.get().strip()

        if token:
            config.set('github', 'token', token)
            config.save()
            self.github_token = token
            messagebox.showinfo("Success", "GitHub token saved successfully!")
            logger.info("GitHub token saved")
        else:
            messagebox.showwarning("Empty Token", "Please enter a token first.")

    def _clear_github_token(self):
        """Clear GitHub token from configuration"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the GitHub token?"):
            config.set('github', 'token', '')
            config.save()
            self.github_token = ''
            self.token_entry.delete(0, tk.END)
            messagebox.showinfo("Success", "GitHub token cleared!")
            logger.info("GitHub token cleared")

    def _check_api_status(self):
        """Check GitHub API rate limit status"""
        url = f"{self.GITHUB_API_BASE}/rate_limit"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DPM-DevTools"
        }

        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))

                core = data['resources']['core']
                remaining = core['remaining']
                limit = core['limit']
                reset_time = datetime.fromtimestamp(core['reset'])

                status_text = f"API Rate Limit: {remaining}/{limit} remaining\n"
                status_text += f"Resets at: {reset_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                status_text += f"Authentication: {'Authenticated' if self.github_token else 'Unauthenticated'}"

                self.api_status_label.config(text=status_text)

        except Exception as e:
            error_msg = f"Error checking API status: {e}"
            logger.error(error_msg)
            self.api_status_label.config(text=error_msg)
