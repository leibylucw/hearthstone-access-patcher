using System;
namespace HSAPatcher;
public struct Source
{
    public readonly string name;
    public readonly string url;
    public Source(string name, string url)
    {
        this.name = name;
        this.url = url;
    }
}

public static class SourceManager
{
    static public Source[] Sources = new Source[]{
        new Source("Default.", "https://hearthstoneaccess.com/files/pre_patch.zip"),
        new Source("Battlegrounds Duos (BETA).", "https://hearthstoneaccess.com/files/duos_beta_patch.zip"),
    };
}
