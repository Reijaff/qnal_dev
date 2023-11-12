rec {
  version = "3.6";
  runtimeInstallScript = src: name:
  ''
    echo Installing ${name}
    addon_path=$XDG_CONFIG_HOME/blender/${version}/scripts/addons/${name}/
    rm -rf $addon_path
    mkdir -p $addon_path
    cp -r ${src}/* $addon_path
    chmod 755 -R $addon_path
  '';

  plugins = [

    rec {
      repo = "MACHIN3tools";
      owner = "machin3io";
      src = builtins.fetchGit {
        url = "https://github.com/${owner}/${repo}";
        rev = "db0590bc624407d07d5c0f08ced2872c04c49d4c";
      };
      ri = runtimeInstallScript src repo;
    }

    rec {
      repo = "import_latex_as_curve";
      owner = "Reijaff";
      src = builtins.fetchGit {
        url = "https://github.com/${owner}/${repo}";
        rev = "3e5776e93f9dc5aa16719520d98377046cd9f73d";
      };
      ri = runtimeInstallScript src repo;
    }

  ];

}
