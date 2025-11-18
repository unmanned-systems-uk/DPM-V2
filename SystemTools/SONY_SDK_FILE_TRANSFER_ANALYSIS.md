# Sony SDK RemoteCli File Transfer Implementation Analysis

**Date:** 2025-11-17
**WHO:** CC-Dev-Tools
**Purpose:** Help Air-Side debug device_handle and file transfer issues
**SDK Version:** CrSDK v2.00.00 (Linux64PC)

---

## Executive Summary

Analysis of Sony's working RemoteCli example reveals **CRITICAL finding**: There is **NO runtime mode switching**. The SDK connects directly in ContentsTransfer mode for file operations. Air-Side's current approach of trying to switch modes after connection may be fundamentally incompatible with the SDK design.

---

## 1. Device Handle Management

### How Device Handle is Obtained

**Location:** `CameraDevice.cpp:235`

```cpp
auto connect_status = SDK::Connect(
    m_info,                    // Camera info
    this,                      // Callback interface (IDeviceCallback*)
    &m_device_handle,          // OUT: Device handle (CrDeviceHandle*)
    openMode,                  // CrSdkControlMode (Remote/ContentsTransfer/RemoteTransfer)
    reconnect,                 // Reconnecting setting
    ...
);
```

**Key Points:**
- `m_device_handle` is an **output parameter** (pointer passed to SDK::Connect)
- SDK populates the handle AFTER successful connection
- Handle type: `std::int64_t` (declared in `CameraDevice.h:318`)

### How Device Handle is Stored

**Location:** `CameraDevice.h:318`

```cpp
class CameraDevice : public SCRSDK::IDeviceCallback
{
private:
    std::int64_t m_device_handle;  // Device handle from SDK::Connect()
    SDK::CrSdkControlMode m_modeSDK;  // Current SDK mode
    // ...
};
```

**Initialization:**
- `CameraDevice.cpp:88`: Initialized to `0` in constructor
- `CameraDevice.cpp:264`: Cleared to `0` on disconnect

### How Device Handle is Used

**Pattern:** Passed as **first parameter** to ALL SDK API calls

**Examples:**

```cpp
// File transfer operations
SDK::GetDateFolderList(m_device_handle, &f_list, &f_nums);
SDK::GetContentsHandleList(m_device_handle, folderHandle, &c_list, &c_nums);
SDK::PullContentsFile(m_device_handle, contentHandle);

// Property operations
SDK::SetDeviceProperty(m_device_handle, &prop);
SDK::GetSelectDeviceProperties(m_device_handle, 1, &getCode, &prop_list, &nprop);

// Command operations
SDK::SendCommand(m_device_handle, commandId, param);
```

**Critical:** Device handle is **NEVER modified** after SDK::Connect() until disconnect.

---

## 2. Mode Switching (RemoteControl ↔ ContentsTransfer)

### 🚨 CRITICAL FINDING: No Runtime Mode Switching

**RemoteCli does NOT switch modes during runtime. It connects directly in the desired mode.**

**Location:** `RemoteCli.cpp:346, 355, 364`

```cpp
// Connect in Remote mode
camera->connect(SDK::CrSdkControlMode_Remote, SDK::CrReconnecting_ON);

// OR connect in ContentsTransfer mode
camera->connect(SDK::CrSdkControlMode_ContentsTransfer, SDK::CrReconnecting_ON);

// OR connect in RemoteTransfer mode (hybrid)
camera->connect(SDK::CrSdkControlMode_RemoteTransfer, SDK::CrReconnecting_ON);
```

### Mode is Specified at Connect Time

**Location:** `CameraDevice.cpp:152`

```cpp
void CameraDevice::connect(SCRSDK::CrSdkControlMode openMode, ...)
{
    // Store requested mode
    m_modeSDK = openMode;

    // Connect with specified mode
    SDK::Connect(m_info, this, &m_device_handle, openMode, ...);
}
```

### Mode is Read-Only After Connection

**Location:** `CameraDevice.cpp:5278-5281`

```cpp
case SDK::CrDevicePropertyCode::CrDeviceProperty_SdkControlMode:
    m_prop.sdk_mode.writable = prop.IsSetEnableCurrentValue();
    m_prop.sdk_mode.current = static_cast<std::uint32_t>(prop.GetCurrentValue());
    m_modeSDK = (SDK::CrSdkControlMode)m_prop.sdk_mode.current;  // Update tracking
    break;
```

**Note:** Mode is READ from properties and tracked, but **NOT SET** via SetDeviceProperty.

### Mode Enum Values

**Location:** `CRSDK/CrDeviceProperty.h:873-878`

```cpp
enum CrSdkControlMode : CrInt32u
{
    CrSdkControlMode_Remote = 0x00000000,          // Remote control only
    CrSdkControlMode_ContentsTransfer,             // 0x00000001 - File transfer only
    CrSdkControlMode_RemoteTransfer,               // 0x00000002 - Hybrid mode
};
```

### To Switch Modes: Disconnect and Reconnect

**Pattern in RemoteCli:**

```
1. User selects different mode in menu
2. camera->disconnect()
3. Return to top menu
4. User selects new connection mode
5. camera->connect(NEW_MODE)
```

**No in-session mode switching found in RemoteCli implementation.**

---

## 3. File Transfer Workflow

### Prerequisites: Check ContentsTransferStatus

**Location:** `CameraDevice.cpp:6036-6054`

```cpp
void CameraDevice::getContentsList()
{
    // STEP 1: Check if Contents Transfer is enabled
    std::int32_t nprop = 0;
    SDK::CrDeviceProperty* prop_list = nullptr;
    CrInt32u getCode = SDK::CrDevicePropertyCode::CrDeviceProperty_ContentsTransferStatus;

    SDK::CrError res = SDK::GetSelectDeviceProperties(
        m_device_handle,
        1,
        &getCode,
        &prop_list,
        &nprop
    );

    bool bExec = false;
    if (CR_SUCCEEDED(res) && (1 == nprop)) {
        if ((getCode == prop_list[0].GetCode()) &&
            (SDK::CrContentsTransfer_ON == prop_list[0].GetCurrentValue()))
        {
            bExec = true;  // Transfer is enabled
        }
        SDK::ReleaseDeviceProperties(m_device_handle, prop_list);
    }

    if (false == bExec) {
        tout << "GetContentsListEnableStatus is Disable. Do it after it becomes Enable.\n";
        return;  // ABORT if not ready
    }

    // Continue with transfer...
}
```

**ContentsTransferStatus Enum:**

```cpp
enum CrContentsTransferStatus : CrInt16u
{
    CrContentsTransfer_OFF = 0x0000,
    CrContentsTransfer_ON,               // 0x0001 - Ready for transfer
};
```

### Step-by-Step File Transfer

**Location:** `CameraDevice.cpp:6067-6133`

```cpp
// STEP 2: Get Date Folder List
CrInt32u f_nums = 0;
SDK::CrMtpFolderInfo* f_list = nullptr;
SDK::CrError err = SDK::GetDateFolderList(m_device_handle, &f_list, &f_nums);

if (CR_SUCCEEDED(err) && 0 < f_nums)
{
    // STEP 3: Iterate through folders
    for (CrInt32u i = 0; i < f_nums; ++i)
    {
        // Store folder info
        auto pFold = new SDK::CrMtpFolderInfo();
        pFold->handle = f_list[i].handle;
        pFold->folderNameSize = f_list[i].folderNameSize;
        pFold->folderName = new CrChar[lenByOS];
        MemCpyEx(pFold->folderName, f_list[i].folderName, lenByOS);

        m_foldList.push_back(pFold);
    }

    // STEP 4: Release folder list (SDK manages memory)
    SDK::ReleaseDateFolderList(m_device_handle, f_list);

    // STEP 5: Get contents handles for each folder
    for (auto folder : m_foldList)
    {
        SDK::CrContentHandle* c_list = nullptr;
        CrInt32u c_nums = 0;

        err = SDK::GetContentsHandleList(
            m_device_handle,
            folder->handle,      // Folder handle from GetDateFolderList
            &c_list,
            &c_nums
        );

        if (CR_SUCCEEDED(err) && 0 < c_nums)
        {
            // STEP 6: Get detailed info for each content
            for (CrInt32u i = 0; i < c_nums; i++)
            {
                SDK::CrMtpContentsInfo* pContents = new SDK::CrMtpContentsInfo();

                err = SDK::GetContentsDetailInfo(
                    m_device_handle,
                    c_list[i],          // Content handle
                    pContents           // OUT: Detailed info
                );

                if (CR_SUCCEEDED(err))
                {
                    m_contentList.push_back(pContents);
                }
            }

            // STEP 7: Release contents handle list
            SDK::ReleaseContentsHandleList(m_device_handle, c_list);
        }
    }
}
```

### Pulling Files

**Location:** `CameraDevice.cpp:6295-6331`

```cpp
void CameraDevice::pullContents(SDK::CrContentHandle content)
{
    // STEP 8: Pull full-size file
    SDK::CrError err = SDK::PullContentsFile(m_device_handle, content);

    if (SDK::CrError_None != err)
    {
        // Error handling
        text id(this->get_id());
        text msg = get_message_desc(err);
        if (!msg.empty()) {
            tout << std::endl << msg.data()
                 << ", handle=" << std::hex << content << std::dec << std::endl;
        }
    }
    // Success: File download triggered, OnNotifyContentsTransfer callback will fire
}
```

**For thumbnails:**

```cpp
void CameraDevice::getScreennail(SDK::CrContentHandle content)
{
    // Pull small-size (thumbnail)
    SDK::CrError err = SDK::PullContentsFile(
        m_device_handle,
        content,
        SDK::CrPropertyStillImageTransSize_SmallSize  // Thumbnail size
    );
}
```

### API Signatures (from CameraRemote_SDK.h)

```cpp
// Get list of date folders
CrError GetDateFolderList(
    CrDeviceHandle deviceHandle,
    CrMtpFolderInfo** folders,      // OUT: Array of folder info
    CrInt32u* numOfFolders          // OUT: Number of folders
);

// Get list of content handles in a folder
CrError GetContentsHandleList(
    CrDeviceHandle deviceHandle,
    CrFolderHandle folderHandle,    // Folder to query
    CrContentHandle** contentHandles, // OUT: Array of content handles
    CrInt32u* numOfContents         // OUT: Number of contents
);

// Pull file from camera
CrError PullContentsFile(
    CrDeviceHandle deviceHandle,
    CrContentHandle contentHandle,  // Content to download
    CrPropertyStillImageTransSize transSize = CrPropertyStillImageTransSize_Original
);
```

---

## 4. Timing and Callbacks

### No Specific Delays for File Transfer

**Finding:** File transfer operations have **NO sleep/wait calls** in RemoteCli.

**Delays ONLY used for remote control operations:**

```cpp
// Example: Shutter operations
std::this_thread::sleep_for(35ms);   // Wait between shutter down/up
std::this_thread::sleep_for(500ms);  // Wait for property changes
std::this_thread::sleep_for(1s);     // Wait for mode changes
```

**File transfer operations rely on callbacks, not polling/delays.**

### Callbacks for File Transfer

**Location:** `CameraDevice.h:298, CameraDevice.cpp:4800`

```cpp
// Callback interface (class inherits from IDeviceCallback)
virtual void OnNotifyContentsTransfer(
    CrInt32u notify,
    SDK::CrContentHandle contentHandle,
    CrChar* filename
) override;
```

**Implementation:**

```cpp
void CameraDevice::OnNotifyContentsTransfer(CrInt32u notify,
                                            SDK::CrContentHandle contentHandle,
                                            CrChar* filename)
{
    // Transfer started
    if (SDK::CrNotify_ContentsTransfer_Start == notify)
    {
        tout << "[START] Contents Handle: 0x" << std::hex << contentHandle << std::dec << std::endl;
    }
    // Transfer completed successfully
    else if (SDK::CrNotify_ContentsTransfer_Complete == notify)
    {
        text file(filename);
        tout << "[COMPLETE] Contents Handle: 0x" << std::hex << contentHandle
             << std::dec << ", File: " << file.data() << std::endl;
    }
    // Transfer failed
    else
    {
        text msg = get_message_desc(notify);
        tout << "[-] Content transfer failure. handle: 0x" << std::hex
             << contentHandle << std::dec << std::endl;
    }
}
```

**Additional Callback:**

```cpp
void CameraDevice::OnCompleteDownload(CrChar* filename, CrInt32u type)
{
    text file(filename);
    tout << "Complete download. File: " << file.data() << '\n';
}
```

### Callback Registration

**Location:** `CameraDevice.cpp:235`

```cpp
// 'this' pointer registers the CameraDevice as the callback handler
SDK::Connect(m_info, this, &m_device_handle, openMode, ...);
//                   ^^^^
//                   IDeviceCallback* - receives all notifications
```

**Pattern:**
1. Call `SDK::PullContentsFile()` → returns immediately
2. SDK starts download in background
3. `OnNotifyContentsTransfer(Start)` fires
4. Download progresses
5. `OnNotifyContentsTransfer(Complete)` fires when done
6. `OnCompleteDownload()` fires with final filename

**No blocking or polling required.**

---

## 5. Comparison with Air-Side POC Implementation

### What Air-Side Likely Does (Hypothesis)

Based on typical patterns:

```cpp
// 1. Connect in Remote mode
SDK::Connect(info, callback, &device_handle, CrSdkControlMode_Remote, ...);

// 2. Do remote control operations
SDK::SendCommand(device_handle, ...);

// 3. Try to switch to ContentsTransfer mode (PROBLEM AREA)
SDK::CrDeviceProperty prop;
prop.SetCode(CrDeviceProperty_SdkControlMode);
prop.SetCurrentValue(CrSdkControlMode_ContentsTransfer);
SDK::SetDeviceProperty(device_handle, &prop);  // ❌ May not work

// 4. Try to transfer files
SDK::GetDateFolderList(device_handle, ...);  // ❌ Fails if mode not switched
```

### What RemoteCli Actually Does

```cpp
// 1. Decide mode BEFORE connecting
CrSdkControlMode mode = CrSdkControlMode_ContentsTransfer;

// 2. Connect directly in ContentsTransfer mode
SDK::Connect(info, callback, &device_handle, mode, ...);

// 3. File transfer immediately available
SDK::GetDateFolderList(device_handle, ...);  // ✅ Works
```

### Key Differences

| Aspect | Air-Side (Hypothesis) | RemoteCli (Actual) |
|--------|----------------------|-------------------|
| **Mode Selection** | Try to switch after connect | Specify at connect time |
| **Connection Flow** | Connect → Switch Mode → Transfer | Connect in mode → Transfer |
| **Mode Switching** | SetDeviceProperty | Disconnect/Reconnect |
| **Device Handle** | Reused across mode changes | New handle per connection |

---

## 6. Critical Insights for Air-Side

### 1. Mode Must Be Set at Connection Time

**Recommendation:** If you need file transfer, connect with `CrSdkControlMode_ContentsTransfer` or `CrSdkControlMode_RemoteTransfer`.

```cpp
// For file transfer only
SDK::Connect(info, callback, &device_handle,
             CrSdkControlMode_ContentsTransfer, ...);

// For remote control AND file transfer
SDK::Connect(info, callback, &device_handle,
             CrSdkControlMode_RemoteTransfer, ...);
```

### 2. Device Handle Lifecycle

**Device handle is tied to connection:**
- Obtained from `SDK::Connect()` (output parameter)
- Stored in member variable
- Passed to ALL subsequent SDK calls
- Invalidated on disconnect (set to 0)

**Pattern:**

```cpp
class MyCamera {
private:
    CrDeviceHandle m_device_handle = 0;

public:
    void connect(CrSdkControlMode mode) {
        SDK::Connect(info, this, &m_device_handle, mode, ...);
        // m_device_handle now valid
    }

    void transfer() {
        SDK::GetDateFolderList(m_device_handle, ...);  // Use handle
    }

    void disconnect() {
        SDK::Disconnect(m_device_handle);
        m_device_handle = 0;  // Invalidate
    }
};
```

### 3. Check ContentsTransferStatus Before Transfer

**Always verify transfer is enabled:**

```cpp
CrInt32u getCode = CrDeviceProperty_ContentsTransferStatus;
SDK::CrDeviceProperty* prop_list = nullptr;
std::int32_t nprop = 0;

SDK::GetSelectDeviceProperties(m_device_handle, 1, &getCode, &prop_list, &nprop);

if (prop_list[0].GetCurrentValue() == CrContentsTransfer_ON) {
    // Safe to call GetDateFolderList, etc.
} else {
    // Wait or abort
}

SDK::ReleaseDeviceProperties(m_device_handle, prop_list);
```

### 4. Use Callbacks, Not Polling

**File transfer is asynchronous:**

```cpp
class MyCamera : public IDeviceCallback {
public:
    void OnNotifyContentsTransfer(CrInt32u notify,
                                  CrContentHandle contentHandle,
                                  CrChar* filename) override {
        if (notify == CrNotify_ContentsTransfer_Complete) {
            // File downloaded successfully
        }
    }

    void downloadFile(CrContentHandle handle) {
        SDK::PullContentsFile(m_device_handle, handle);
        // Returns immediately, callback fires when done
    }
};
```

### 5. Memory Management

**SDK allocates, you release:**

```cpp
// GetDateFolderList allocates f_list
SDK::CrMtpFolderInfo* f_list = nullptr;
CrInt32u f_nums = 0;
SDK::GetDateFolderList(m_device_handle, &f_list, &f_nums);

// Your code uses f_list...

// YOU must release it
SDK::ReleaseDateFolderList(m_device_handle, f_list);

// Same for GetContentsHandleList
SDK::ReleaseContentsHandleList(m_device_handle, c_list);
```

---

## 7. Recommended Workflow for Air-Side

### If You Need BOTH Remote Control and File Transfer

**Option A: Use RemoteTransfer Mode (Hybrid)**

```cpp
// 1. Connect in hybrid mode
SDK::Connect(info, callback, &device_handle,
             CrSdkControlMode_RemoteTransfer, ...);

// 2. Remote control available
SDK::SendCommand(device_handle, CrCommandId_Release, ...);

// 3. File transfer available (when ContentsTransferStatus == ON)
SDK::GetDateFolderList(device_handle, ...);
```

**Option B: Disconnect and Reconnect**

```cpp
// 1. Connect in Remote mode for shooting
SDK::Connect(info, callback, &device_handle,
             CrSdkControlMode_Remote, ...);
SDK::SendCommand(device_handle, CrCommandId_Release, ...);

// 2. Disconnect
SDK::Disconnect(device_handle);
device_handle = 0;

// 3. Reconnect in ContentsTransfer mode for files
SDK::Connect(info, callback, &device_handle,
             CrSdkControlMode_ContentsTransfer, ...);
SDK::GetDateFolderList(device_handle, ...);

// 4. Disconnect when done
SDK::Disconnect(device_handle);
```

### If You Only Need File Transfer

```cpp
// 1. Connect in ContentsTransfer mode
SDK::Connect(info, callback, &device_handle,
             CrSdkControlMode_ContentsTransfer, ...);

// 2. Check status
CrInt32u getCode = CrDeviceProperty_ContentsTransferStatus;
SDK::GetSelectDeviceProperties(device_handle, 1, &getCode, &prop_list, &nprop);
if (prop_list[0].GetCurrentValue() != CrContentsTransfer_ON) {
    // Wait or retry
}
SDK::ReleaseDeviceProperties(device_handle, prop_list);

// 3. Get folder list
SDK::CrMtpFolderInfo* f_list = nullptr;
CrInt32u f_nums = 0;
SDK::GetDateFolderList(device_handle, &f_list, &f_nums);

// 4. Get contents list for each folder
for (CrInt32u i = 0; i < f_nums; ++i) {
    SDK::CrContentHandle* c_list = nullptr;
    CrInt32u c_nums = 0;
    SDK::GetContentsHandleList(device_handle, f_list[i].handle, &c_list, &c_nums);

    // 5. Pull files
    for (CrInt32u j = 0; j < c_nums; ++j) {
        SDK::PullContentsFile(device_handle, c_list[j]);
        // Callback will fire when complete
    }

    SDK::ReleaseContentsHandleList(device_handle, c_list);
}

SDK::ReleaseDateFolderList(device_handle, f_list);

// 6. Disconnect
SDK::Disconnect(device_handle);
```

---

## 8. Error Handling

### Warning Codes for ContentsTransfer

**Location:** `CameraDevice.cpp:4833-4841`

```cpp
case SDK::CrWarning_ContentsTransferMode_Invalid:
case SDK::CrWarning_ContentsTransferMode_DeviceBusy:
case SDK::CrWarning_ContentsTransferMode_StatusError:
    tout << "\nThe camera is in a condition where it cannot transfer content.\n\n";
    tout << "Please input '0' to return to the TOP-MENU and connect again.\n";
    break;

case SDK::CrWarning_ContentsTransferMode_CanceledFromCamera:
    // Transfer canceled by user on camera
    break;
```

**Recommendation:** Monitor `OnWarning()` callback for these codes.

---

## 9. Summary of Key Takeaways

✅ **Device handle is obtained from SDK::Connect() as output parameter**
✅ **Device handle is stored in member variable, passed to all SDK calls**
✅ **Mode is specified AT CONNECT TIME, not switched during session**
✅ **To change modes: disconnect and reconnect**
✅ **Always check ContentsTransferStatus before file transfer**
✅ **File transfer uses callbacks, not polling/delays**
✅ **SDK allocates memory, you must release it (ReleaseDateFolderList, etc.)**
✅ **RemoteTransfer mode allows both remote control AND file transfer**

---

## 10. Files Referenced

| File | Location | Purpose |
|------|----------|---------|
| **RemoteCli.cpp** | ~/Sony_SDK/.../app/RemoteCli.cpp | CLI application, menu system |
| **CameraDevice.cpp** | ~/Sony_SDK/.../app/CameraDevice.cpp | Camera device implementation |
| **CameraDevice.h** | ~/Sony_SDK/.../app/CameraDevice.h | Device class interface |
| **CameraRemote_SDK.h** | ~/Sony_SDK/.../app/CRSDK/CameraRemote_SDK.h | SDK API signatures |
| **CrDeviceProperty.h** | ~/Sony_SDK/.../app/CRSDK/CrDeviceProperty.h | Enums, property codes |
| **IDeviceCallback.h** | ~/Sony_SDK/.../app/CRSDK/IDeviceCallback.h | Callback interface |

---

**END OF ANALYSIS**

**Next Steps for Air-Side:**
1. Review current connection/mode logic
2. Verify device_handle is obtained from SDK::Connect() output parameter
3. Consider using `CrSdkControlMode_RemoteTransfer` for hybrid functionality
4. Implement `OnNotifyContentsTransfer` callback if not already present
5. Remove any attempts to switch modes via SetDeviceProperty
6. Test with ContentsTransfer mode connection
