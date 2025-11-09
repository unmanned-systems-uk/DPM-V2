"""
Git Helper Tab for DPM Diagnostic Tool
Simplifies git operations - pull, commit, and push with one click
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
from pathlib import Path
from datetime import datetime

from utils.logger import logger


class GitHelperTab(ttk.Frame):
    """Git Helper tab - simplifies git operations for non-git users"""

    # Git domain tags
    DOMAIN_TAGS = [
        "[DOCS]",
        "[AIR]",
        "[GROUND]",
        "[TOOLS]",
        "[PM]",
        "[PROTOCOL]"
    ]

    # Git type tags
    TYPE_TAGS = [
        "[FEATURE]",
        "[FIX]",
        "[REFACTOR]",
        "[TEST]",
        "[BUILD]",
        "[WIP]",
        "[DEPLOYMENT]"
    ]

    def __init__(self, parent):
        super().__init__(parent)

        # Repository path
        self.repo_path = Path(__file__).parent.parent.parent

        # Variables
        self.domain_var = tk.StringVar(value="[DOCS]")
        self.type_var = tk.StringVar(value="[DEPLOYMENT]")
        self.message_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Not checked")
        self.branch_var = tk.StringVar(value="Unknown")
        self.ahead_var = tk.StringVar(value="Unknown")
        self.behind_var = tk.StringVar(value="Unknown")

        self._create_ui()
        self._refresh_status()

        logger.debug("Git Helper tab initialized")

    def _create_ui(self):
        """Create UI elements"""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Git Helper - Simplified Git Operations",
            font=("TkDefaultFont", 12, "bold")
        )
        title_label.pack(pady=(0, 10))

        # Status section
        self._create_status_section(main_frame)

        # Staged files section
        self._create_staged_files_section(main_frame)

        # Commit message section
        self._create_commit_message_section(main_frame)

        # Action buttons
        self._create_action_buttons(main_frame)

        # Output section
        self._create_output_section(main_frame)

    def _create_status_section(self, parent):
        """Create repository status section"""
        status_frame = ttk.LabelFrame(parent, text="📊 Repository Status", padding=10)
        status_frame.pack(fill=tk.X, pady=(0, 10))

        # Repository path
        repo_label = ttk.Label(
            status_frame,
            text=f"Repository: {self.repo_path}",
            font=("TkDefaultFont", 9)
        )
        repo_label.pack(anchor=tk.W)

        # Status grid
        status_grid = ttk.Frame(status_frame)
        status_grid.pack(fill=tk.X, pady=(5, 0))

        # Branch
        ttk.Label(status_grid, text="Branch:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.branch_label = ttk.Label(status_grid, textvariable=self.branch_var, font=("TkDefaultFont", 9, "bold"))
        self.branch_label.grid(row=0, column=1, sticky=tk.W)

        # Ahead/Behind
        ttk.Label(status_grid, text="Ahead:").grid(row=0, column=2, sticky=tk.W, padx=(20, 5))
        self.ahead_label = ttk.Label(status_grid, textvariable=self.ahead_var)
        self.ahead_label.grid(row=0, column=3, sticky=tk.W)

        ttk.Label(status_grid, text="Behind:").grid(row=0, column=4, sticky=tk.W, padx=(10, 5))
        self.behind_label = ttk.Label(status_grid, textvariable=self.behind_var)
        self.behind_label.grid(row=0, column=5, sticky=tk.W)

        # Status
        ttk.Label(status_grid, text="Status:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.status_label = ttk.Label(status_grid, textvariable=self.status_var)
        self.status_label.grid(row=1, column=1, columnspan=5, sticky=tk.W, pady=(5, 0))

    def _create_staged_files_section(self, parent):
        """Create staged files section"""
        files_frame = ttk.LabelFrame(parent, text="📝 Staged Files (Ready to Commit)", padding=10)
        files_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Files listbox with scrollbar
        list_frame = ttk.Frame(files_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.files_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            height=6,
            selectmode=tk.SINGLE
        )
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.files_listbox.yview)

    def _create_commit_message_section(self, parent):
        """Create commit message section"""
        message_frame = ttk.LabelFrame(parent, text="💬 Commit Message", padding=10)
        message_frame.pack(fill=tk.X, pady=(0, 10))

        # Tag selectors
        tag_frame = ttk.Frame(message_frame)
        tag_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(tag_frame, text="Domain:").pack(side=tk.LEFT, padx=(0, 5))
        domain_combo = ttk.Combobox(
            tag_frame,
            textvariable=self.domain_var,
            values=self.DOMAIN_TAGS,
            state="readonly",
            width=12
        )
        domain_combo.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(tag_frame, text="Type:").pack(side=tk.LEFT, padx=(0, 5))
        type_combo = ttk.Combobox(
            tag_frame,
            textvariable=self.type_var,
            values=self.TYPE_TAGS,
            state="readonly",
            width=15
        )
        type_combo.pack(side=tk.LEFT)

        # Message entry
        msg_frame = ttk.Frame(message_frame)
        msg_frame.pack(fill=tk.X)

        ttk.Label(msg_frame, text="Description:").pack(side=tk.LEFT, padx=(0, 5))
        message_entry = ttk.Entry(msg_frame, textvariable=self.message_var, width=50)
        message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Preview
        self.preview_label = ttk.Label(
            message_frame,
            text="Preview: [DOCS][DEPLOYMENT] Your message here",
            font=("TkDefaultFont", 9, "italic"),
            foreground="gray"
        )
        self.preview_label.pack(anchor=tk.W, pady=(5, 0))

        # Update preview when tags or message changes
        self.domain_var.trace_add("write", self._update_preview)
        self.type_var.trace_add("write", self._update_preview)
        self.message_var.trace_add("write", self._update_preview)

    def _create_action_buttons(self, parent):
        """Create action buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        # Pull button
        pull_btn = ttk.Button(
            button_frame,
            text="🔄 Pull Latest",
            command=self._pull_latest,
            width=20
        )
        pull_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Commit & Push button (primary action)
        commit_push_btn = ttk.Button(
            button_frame,
            text="💾 Commit & Push",
            command=self._commit_and_push,
            width=20,
        )
        commit_push_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Refresh status button
        refresh_btn = ttk.Button(
            button_frame,
            text="🔍 Refresh Status",
            command=self._refresh_status,
            width=20
        )
        refresh_btn.pack(side=tk.LEFT)

    def _create_output_section(self, parent):
        """Create output section"""
        output_frame = ttk.LabelFrame(parent, text="📋 Output", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True)

        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            height=10,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Configure tags for colored output
        self.output_text.tag_config("success", foreground="green")
        self.output_text.tag_config("error", foreground="red")
        self.output_text.tag_config("warning", foreground="orange")
        self.output_text.tag_config("info", foreground="blue")

    def _update_preview(self, *args):
        """Update commit message preview"""
        domain = self.domain_var.get()
        type_tag = self.type_var.get()
        message = self.message_var.get()

        if message:
            preview = f"{domain}{type_tag} {message}"
        else:
            preview = f"{domain}{type_tag} Your message here"

        self.preview_label.config(text=f"Preview: {preview}")

    def _append_output(self, text, tag="info"):
        """Append text to output area"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text + "\n", tag)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def _run_git_command(self, command, description=""):
        """Run a git command and return output"""
        try:
            if description:
                self._append_output(f"\n> {description}...", "info")

            result = subprocess.run(
                command,
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                shell=True
            )

            # Show output
            if result.stdout.strip():
                self._append_output(result.stdout.strip(), "info")

            if result.stderr.strip():
                # Some git messages go to stderr even on success
                self._append_output(result.stderr.strip(), "warning")

            if result.returncode == 0:
                if description:
                    self._append_output(f"✅ {description} successful!", "success")
                return True, result.stdout
            else:
                self._append_output(f"❌ {description} failed!", "error")
                return False, result.stderr

        except Exception as e:
            self._append_output(f"❌ Error: {str(e)}", "error")
            logger.error(f"Git command failed: {e}")
            return False, str(e)

    def _refresh_status(self):
        """Refresh git repository status"""
        def refresh_thread():
            try:
                # Get current branch
                success, output = self._run_git_command(
                    "git branch --show-current",
                    "Checking branch"
                )
                if success:
                    branch = output.strip()
                    self.branch_var.set(branch if branch else "detached")

                    # Warn if not on main
                    if branch != "main":
                        self.branch_label.config(foreground="orange")
                        self._append_output(
                            f"⚠️  Warning: You are on branch '{branch}', not 'main'",
                            "warning"
                        )
                    else:
                        self.branch_label.config(foreground="black")

                # Get ahead/behind status
                success, output = self._run_git_command(
                    "git status -sb",
                    "Checking sync status"
                )
                if success:
                    # Parse ahead/behind from output
                    if "ahead" in output:
                        ahead = output.split("ahead")[1].split("]")[0].strip()
                        self.ahead_var.set(ahead)
                    else:
                        self.ahead_var.set("0")

                    if "behind" in output:
                        behind = output.split("behind")[1].split("]")[0].strip()
                        self.behind_var.set(behind)
                        self.behind_label.config(foreground="orange")
                    else:
                        self.behind_var.set("0")
                        self.behind_label.config(foreground="black")

                # Get file status
                success, output = self._run_git_command(
                    "git status --short",
                    "Checking file status"
                )
                if success:
                    lines = output.strip().split("\n") if output.strip() else []

                    # Filter out .claude/settings.local.json
                    staged_files = []
                    for line in lines:
                        if line.strip() and ".claude/settings.local.json" not in line:
                            staged_files.append(line.strip())

                    # Update files listbox
                    self.files_listbox.delete(0, tk.END)
                    for file in staged_files:
                        self.files_listbox.insert(tk.END, file)

                    # Update status
                    if staged_files:
                        self.status_var.set(f"{len(staged_files)} file(s) changed")
                    else:
                        self.status_var.set("No changes to commit")

                self._append_output("✅ Status refresh complete", "success")

            except Exception as e:
                self._append_output(f"❌ Error refreshing status: {str(e)}", "error")
                logger.error(f"Status refresh failed: {e}")

        threading.Thread(target=refresh_thread, daemon=True).start()

    def _pull_latest(self):
        """Pull latest changes from remote"""
        def pull_thread():
            try:
                self._append_output("\n" + "="*60, "info")
                self._append_output("PULLING LATEST CHANGES", "info")
                self._append_output("="*60, "info")

                # Pull from origin main
                success, output = self._run_git_command(
                    "git pull origin main",
                    "Pulling from origin/main"
                )

                if success:
                    # Refresh status after pull
                    self._refresh_status()
                else:
                    self._append_output(
                        "⚠️  Pull failed - please resolve conflicts manually",
                        "error"
                    )

            except Exception as e:
                self._append_output(f"❌ Error pulling: {str(e)}", "error")
                logger.error(f"Pull failed: {e}")

        threading.Thread(target=pull_thread, daemon=True).start()

    def _commit_and_push(self):
        """Commit and push changes in one operation"""
        # Validate commit message
        message = self.message_var.get().strip()
        if not message:
            messagebox.showwarning(
                "No Message",
                "Please enter a commit message description"
            )
            return

        # Get full commit message
        domain = self.domain_var.get()
        type_tag = self.type_var.get()
        full_message = f"{domain}{type_tag} {message}"

        def commit_push_thread():
            try:
                self._append_output("\n" + "="*60, "info")
                self._append_output("COMMIT & PUSH WORKFLOW", "info")
                self._append_output("="*60, "info")

                # Step 1: Pull latest (to prevent "behind" errors)
                success, output = self._run_git_command(
                    "git pull origin main",
                    "Step 1: Pull latest changes"
                )
                if not success:
                    self._append_output("⚠️  Failed to pull - stopping workflow", "error")
                    return

                # Step 2: Add all changed files (except .claude/settings.local.json)
                success, output = self._run_git_command(
                    "git add .",
                    "Step 2: Stage changes"
                )
                if not success:
                    self._append_output("⚠️  Failed to stage files - stopping workflow", "error")
                    return

                # Step 3: Commit with message
                commit_command = f'git commit -m "{full_message}"'
                success, output = self._run_git_command(
                    commit_command,
                    "Step 3: Commit changes"
                )
                if not success:
                    # Check if it's "nothing to commit"
                    if "nothing to commit" in output.lower():
                        self._append_output("ℹ️  No changes to commit", "warning")
                        return
                    else:
                        self._append_output("⚠️  Failed to commit - stopping workflow", "error")
                        return

                # Step 4: Push to remote
                success, output = self._run_git_command(
                    "git push origin main",
                    "Step 4: Push to GitHub"
                )
                if success:
                    self._append_output("\n" + "="*60, "success")
                    self._append_output("✅ SUCCESS - All changes pushed to GitHub!", "success")
                    self._append_output("="*60, "success")

                    # Clear commit message
                    self.message_var.set("")

                    # Refresh status
                    self._refresh_status()
                else:
                    self._append_output("⚠️  Failed to push - please check errors above", "error")

            except Exception as e:
                self._append_output(f"❌ Error in commit/push workflow: {str(e)}", "error")
                logger.error(f"Commit/push failed: {e}")

        threading.Thread(target=commit_push_thread, daemon=True).start()
