using Robust.Shared;
using Robust.Shared.Configuration;

namespace Content.Shared._Moffstation.CCVar;

[CVarDefs]
public sealed class MoffCCVars
{
    /// <summary>
    ///     How many times post-round can be extended by vote. 0 disables the vote.
    /// </summary>
    public static readonly CVarDef<int> MaxRoundEndExtensionVotes =
        CVarDef.Create("moff.round_end_extension_max", 2, CVar.SERVERONLY);

    /// <summary>
    ///     How many minutes each successful post-round extension vote extends the round by.
    /// </summary>
    public static readonly CVarDef<int> RoundEndExtensionVoteMinutes =
        CVarDef.Create("moff.round_end_extension_minutes", 5, CVar.SERVERONLY);

    /// <summary>
    ///     How long the extension vote stays open, in seconds.
    /// </summary>
    public static readonly CVarDef<int> RoundEndExtensionVoteDuration =
        CVarDef.Create("moff.round_end_extension_duration", 30, CVar.SERVERONLY);

}
