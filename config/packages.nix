{
  pkgs,
  ...
}:
{
  packages = with pkgs; [
    pulumi-esc
  ];
}
