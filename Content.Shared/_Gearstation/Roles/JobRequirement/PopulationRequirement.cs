using Content.Shared.Preferences;
using JetBrains.Annotations;
using Robust.Shared.Player;
using Robust.Shared.Prototypes;
using Robust.Shared.Serialization;
using Robust.Shared.Utility;

namespace Content.Shared.Roles;

/// <summary>
/// Requires a certain amount of players in the server (NOT INCLUSIVE)
/// </summary>
[UsedImplicitly]
[Serializable, NetSerializable]
public sealed partial class PopulationRequirement : JobRequirement
{
    [DataField(required: true)]
    public int RequiredPopulation;
    private static ISharedPlayerManager? _playerManager;

    public override bool Check(IEntityManager entManager,
        ICommonSession? player,
        IPrototypeManager protoManager,
        HumanoidCharacterProfile? profile,
        IReadOnlyDictionary<string, TimeSpan>? playTimes,
        out FormattedMessage reason)
    {
        reason = new FormattedMessage();

        if (profile is null)
            return true;

        _playerManager ??= IoCManager.Resolve<ISharedPlayerManager>();
        int playerCount = _playerManager.PlayerCount;

        reason = FormattedMessage.FromMarkupPermissive(Loc.GetString(
            Inverted ? "role-timer-pop-low-enough" : "role-timer-pop-high-enough",
            ("pop", RequiredPopulation)));

        if (!Inverted)
        {
            if (playerCount > RequiredPopulation)
                return true;

            reason = FormattedMessage.FromMarkupPermissive(Loc.GetString("role-timer-pop-not-high-enough",
                ("pop", RequiredPopulation)));
            return false;
        }
        else
        {
            if (playerCount < RequiredPopulation)
                return true;

            reason = FormattedMessage.FromMarkupPermissive(Loc.GetString("role-timer-pop-not-low-enough",
                ("pop", RequiredPopulation)));
            return false;
        }
    }
}
