{
  processes = {
    devenv-info = {
      exec = "devenv info";
      process-compose = {
        is_tty = true;
        disabled = false;
        namespace = "🩺 HEALTH CHECK";
        description = "❄ devenv info";
      };
    };

    docs = {
      exec = "docs";
      process-compose = {
        is_tty = true;
        disabled = true;
        namespace = "📚 DOCS";
      };
    };
  };

  process = {
    manager.args = {
      "theme" = "One Dark";
    };

    managers.process-compose.settings.availability = {
      max_restarts = 5;
      backoff_seconds = 2;
      restart = "on_failure";
    };
  };
}
