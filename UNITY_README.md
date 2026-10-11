# Wipkingen Nuisance Tracker - Unity APK Integration Guide

Because the data is small and the Folium logic has been rewritten in pure JavaScript, this map can run **completely independently** on an Android phone as a native APK compiled from Unity, without needing a Python backend!

## Prerequisites
1. **Unity 6** (or any modern Unity version).
2. A Unity WebView Plugin. (Because standard Unity UI does not render HTML/JS, you need a plugin. The two industry standards are **[Vuplex 3D WebView for Android](https://developer.vuplex.com/)** or **[UniWebView](https://uniwebview.com/)**. This guide uses UniWebView syntax, as it is very popular for 2D mobile apps).

---

## Setup Instructions

### 1. Place the Assets
Copy the entire `unity_assets` folder from this repository and place its contents directly into your Unity project's `StreamingAssets` folder.
*(If the folder doesn't exist, create it: `Assets/StreamingAssets/`)*

Your folder structure should look like this:
```
YourUnityProject/
  Assets/
    StreamingAssets/
      index.html
      app.js
      historical_data.json
```

### 2. Configure Unity for Android
- Open Unity. Go to **File -> Build Settings**.
- Switch Platform to **Android**.
- Under **Player Settings -> Internet Access**, ensure it is set to **Require**. (The app needs internet to fetch the live Open311 JSON updates and load the OpenStreetMap map tiles).

### 3. Create the C# WebView Controller
Create a new C# Script in Unity called `MapAppController.cs`. Attach it to an empty GameObject in your main scene.

Here is the exact code to load your local `index.html` file into the mobile app:

```csharp
using UnityEngine;
// using Vuplex.WebView; // Uncomment if using Vuplex
// using UniWebView; // Uncomment if using UniWebView

public class MapAppController : MonoBehaviour
{
    // If using UniWebView:
    private UniWebView webView;

    void Start()
    {
        // 1. Create the WebView component
        var webViewGameObject = new GameObject("UniWebView");
        webView = webViewGameObject.AddComponent<UniWebView>();

        // 2. Make it fill the entire screen of the phone
        webView.ReferenceRectTransform = this.GetComponent<RectTransform>(); // Or specify screen bounds manually
        webView.Frame = new Rect(0, 0, Screen.width, Screen.height);

        // 3. Define the path to the standalone HTML file in StreamingAssets
        string localUrl = "";
#if UNITY_ANDROID
        localUrl = "file:///android_asset/index.html";
#elif UNITY_IOS
        localUrl = "file://" + Application.streamingAssetsPath + "/index.html";
#else
        localUrl = "file://" + Application.streamingAssetsPath + "/index.html";
#endif

        // 4. Load the URL and show it
        webView.Load(localUrl);
        webView.Show();
    }
}
```

### 4. Build and Run!
- Connect your Android phone via USB.
- In Unity, hit **Build And Run**.
- Unity will compile the `.apk` file, transfer it to your phone, and install the icon.
- When you open the app, the C# script instantly mounts a native Android browser instance, points it to the local `index.html` bundle, and Leaflet renders your map flawlessly.
- Pressing "Refresh Live Data" executes the JavaScript `fetch()` command, directly grabbing the latest reports from the city of Zurich servers.