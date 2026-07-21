"""CLI wrapper for the packaged default-deny plugin manifest validator."""

from upi.plugin_loader import AngelicaPluginLoader

if __name__ == "__main__":
    loader = AngelicaPluginLoader("oden.json")
    print(f"Validated {loader.manifest['pluginId']} in {loader.manifest['mode']} mode")
