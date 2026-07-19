import json
import os
import subprocess
from typing import Dict


class AngelicaPluginLoader:
    def __init__(self, manifest_path: str):
        with open(manifest_path, 'r') as f:
            self.manifest: Dict = json.load(f)
        self.validate()

    def validate(self):
        # In a real impl, use jsonschema
        required = ["pluginId", "version", "entryPoint", "runtime", "permissions"]
        for field in required:
            if field not in self.manifest:
                raise ValueError(f"Missing required field: {field}")

        # Deny host-level access: network must not be 'host' (string mode) and
        # mounts must not be root '/' (only relevant when specified as a string path).
        network_val = self.manifest['permissions'].get('network')
        mounts_val = self.manifest['permissions'].get('mounts')
        if network_val == 'host' or mounts_val == '/':
            raise PermissionError("Forbidden: network=host or mounts=/ is not allowed")

    def spawn(self):
        print(f"Spawning sandboxed container for {self.manifest['pluginId']}...")
        # Mocking container spawn
        cmd = [
            "docker", "run", "-d",
            "--name", self.manifest['pluginId'],
            "--memory", self.manifest.get('resources', {}).get('memory', '512m'),
            "vrasi1-plugin-base",
        ]
        print(f"Executing: {' '.join(cmd)}")
        # subprocess.run(cmd)  # Disabled for scaffold


if __name__ == "__main__":
    loader = AngelicaPluginLoader("oden.json")
    loader.spawn()
