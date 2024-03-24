rec {
  runtimeInstallScript = src: name: ''
    echo Installing ${name}

    # addon_path=$XDG_CONFIG_HOME/blender/4.0/scripts/addons/${name}/
    addon_path=$XDG_CONFIG_HOME/bforartists/4.1/scripts/addons/${name}/
    rm -rf $addon_path
    mkdir -p $addon_path
    cp -r ${src}/* $addon_path
    chmod 755 -R $addon_path
  '';

  plugins = [
    # rec {
    # repo = "MACHIN3tools";
    # owner = "machin3io";
    # src = builtins.fetchGit {
    # url = "https://github.com/${owner}/${repo}";
    # rev = "";
    # };
    # ri = runtimeInstallScript src repo;
    # }

    rec {
      repo = "import_latex_as_curve";
      owner = "Reijaff";
      src = builtins.fetchGit {
        url = "https://github.com/${owner}/${repo}";
        rev = "c699829e6da3983acb7366bd200a9550fbeef60a";
      };
      ri = runtimeInstallScript src repo;
    }

    rec {
      repo = "marking_of_highlights";
      owner = "Reijaff";
      src = builtins.fetchGit {
        url = "https://github.com/${owner}/${repo}";
        rev = "7e0e2b229c9886fe3f5beafb04cbf0f284e75ab5";
      };
      ri = runtimeInstallScript src repo;
    }

    rec {
      repo = "bake_audio_frequencies";
      owner = "Reijaff";
      src = builtins.fetchGit {
        url = "https://github.com/${owner}/${repo}";
        rev = "5cb875600a0533c517307421df58a8c7883e7f75";
      };
      ri = runtimeInstallScript src repo;
    }

    rec {
      repo = "combine_edits";
      owner = "Reijaff";
      src = builtins.fetchGit {
        url = "https://github.com/${owner}/${repo}";
        rev = "a114363629a2fb9190db50eb3895f9a82e93dd43";
      };
      ri = runtimeInstallScript src repo;
    }

    rec {
      repo = "add_scene_with_sound";
      owner = "Reijaff";
      src = builtins.fetchGit {
        url = "https://github.com/${owner}/${repo}";
        rev = "2d534ae82af0f3a4b836b58ff7805756709b9445";
      };
      ri = runtimeInstallScript src repo;
    }

    rec {
      repo = "plane_quad_mask";
      owner = "Reijaff";
      src = builtins.fetchGit {
        url = "https://github.com/${owner}/${repo}";
        rev = "7bcea50f0b4ba785636a2bfa2a5902068f5beeba";
      };
      ri = runtimeInstallScript src repo;
    }

    rec {
      repo = "tts_client";
      owner = "Reijaff";
      src = builtins.fetchGit {
        url = "https://github.com/${owner}/${repo}";
        rev = "b87b6811a1753af19b8f886163875524d2f0e7ec";
      };
      ri = runtimeInstallScript src repo;
    }
  ];
}
