{
  config,
  ...
}:
{

  scripts = {
    kernel = {
      description = " 🎉 Fire up the Microvisor Kernel";
      exec = "devenv up";
    };

    docs = {
      description = " 📚 RTFM";
      exec = "pnpx likec4 start ${config.env.DEVENV_ROOT}/docs";
    };

    dev = {
      exec = "uv run ${config.env.DEVENV_ROOT}/src/main.py";
    };
  };
}
