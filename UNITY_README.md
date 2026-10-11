# Wipkingen Nuisance Tracker - Unity APK Integration Guide

Because the data is small and the Folium logic has been rewritten in pure JavaScript, this map can run **completely independently** on an Android phone as a native APK compiled from Unity!

Since standard Unity UI does not render HTML/JS, we will use the free, open-source **[gree/unity-webview](https://github.com/gree/unity-webview)** plugin to display our Leaflet map.

---

## 1. Install the Free WebView Plugin
To fix any `CS0246` errors, you must install the free webview plugin into your Unity 6 project.

1. In Unity, go to **Window -> Package Manager**.
2. Click the **`+`** button (top left corner) and select **"Add package from git URL..."**.
3. Paste the following exact URL (including the path parameter) and click **Add**:
   `https://github.com/gree/unity-webview.git?path=/dist/package`

### 1.5 Fix Assembly References (CS0246 Error)
Because you installed the plugin via the Package Manager, Unity isolates its scripts into a separate assembly. To allow your scripts to "see" `WebViewObject`, you must link the assemblies:
1. Go to your `Assets/Scripts` folder (or wherever you placed your `MapAppController.cs` script).
2. Go to **Assets > Create > Scripting > Assembly Definition** in the top menu bar. Name it `MapAppAssembly`.
3. Select your new `MapAppAssembly` file.
4. In the Inspector, under **Assembly Definition References**, click the `+` button.
5. Click the tiny circle/target icon in the new slot, and select `unity-webview`. (Do NOT type `net.gree.unity-webview`).
6. Click **Apply** at the bottom of the Inspector.

*(Note: The gree webview plugin relies on a native iOS/Android bridge. You will only see the map when you Build and Run to your Android phone, or run in the Mac/Windows editor if the native binaries are present. It is designed to work flawlessly on the Android device).*

---

## 2. Place the Map Assets
Copy the entire `unity_assets` folder from this repository and place its contents directly into your Unity project's `StreamingAssets` folder.
*(If the folder doesn't exist, create it: `Assets/StreamingAssets/`)*

Your folder structure **must** look exactly like this:
```
YourUnityProject/
  Assets/
    StreamingAssets/
      index.html
      app.js
      historical_data.json
```

---

## 3. Configure Unity for Android
- Open Unity. Go to **File -> Build Settings**.
- Switch Platform to **Android**.
- Go to **Player Settings -> Internet Access** and ensure it is set to **Require**. (The app needs internet to fetch the live Open311 updates and map tiles).
- In Player Settings, ensure **Write Permission** is set to **External (SDCard)** if prompted, though default usually works for StreamingAssets reading.

---

## 4. Create the C# Controller
Create a new C# Script in Unity called `MapAppController.cs`.
Attach this script to an **empty GameObject** in your main scene (e.g., name the GameObject "MapManager").

Copy and paste this exact code. It is designed specifically for the `gree/unity-webview` plugin:

```csharp
using UnityEngine;
using System.IO;

public class MapAppController : MonoBehaviour
{
    private WebViewObject webViewObject;

    void Start()
    {
        // 1. Create the WebViewObject component
        webViewObject = (new GameObject("WebViewObject")).AddComponent<WebViewObject>();

        // 2. Initialize the webview with basic callbacks (optional but good for debugging)
        webViewObject.Init(
            cb: (msg) => Debug.Log(string.Format("CallFromJS[{0}]", msg)),
            err: (msg) => Debug.Log(string.Format("CallOnError[{0}]", msg)),
            httpErr: (msg) => Debug.Log(string.Format("CallOnHttpError[{0}]", msg)),
            started: (msg) => Debug.Log(string.Format("CallOnStarted[{0}]", msg)),
            hooked: (msg) => Debug.Log(string.Format("CallOnHooked[{0}]", msg)),
            ld: (msg) => {
                Debug.Log(string.Format("CallOnLoaded[{0}]", msg));
                // Show the webview once it's fully loaded
                webViewObject.SetVisibility(true);
            }
        );

        // 3. Make it fill the entire screen (margins: left, top, right, bottom)
        webViewObject.SetMargins(0, 0, 0, 0);

        // 4. Define the path to the standalone HTML file in StreamingAssets
        string localUrl;

#if UNITY_EDITOR_WIN || UNITY_STANDALONE_WIN
        localUrl = "file:///" + Application.streamingAssetsPath.Replace("\\", "/") + "/index.html";
#elif UNITY_EDITOR_OSX || UNITY_STANDALONE_OSX
        localUrl = "file://" + Application.streamingAssetsPath + "/index.html";
#elif UNITY_ANDROID
        // Android requires a specific format for local streaming assets in gree webview
        localUrl = "file:///android_asset/index.html";
#elif UNITY_IOS
        localUrl = "file://" + Application.streamingAssetsPath + "/index.html";
#else
        localUrl = "file://" + Application.streamingAssetsPath + "/index.html";
#endif

        // 5. Load the URL
        webViewObject.LoadURL(localUrl);
    }

    void OnDestroy()
    {
        if (webViewObject != null)
        {
            Destroy(webViewObject.gameObject);
        }
    }
}
```

---

## 5. Build and Run
1. Connect your Android phone via USB.
2. In Unity, hit **File -> Build And Run**.
3. Unity will compile the `.apk` file and install it on your phone.
4. When you open the app, it will display the Leaflet heatmap flawlessly.
5. Pressing "Refresh Live Data" executes the JavaScript `fetch()` command, directly grabbing the latest reports from the city of Zurich!