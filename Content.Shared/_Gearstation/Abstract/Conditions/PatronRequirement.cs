using Robust.Shared.Player;
using Content.Shared._Starlight.Abstract.Conditions;

namespace Content.Shared._Gearstation.Abstract.Conditions;

/// <summary>
/// Requires the player to have a Patreon tier.
/// </summary>
public sealed partial class PatronRequirement : BaseRequirement
{
    public override string GetRequirementDescription()
    {
        base.GetRequirementDescription();
        return Loc.GetString("requirements-patron");
    }

    public override bool Handle(ICommonSession user)
    {
        base.Handle(user);
        return user.Channel.UserData.PatronTier is { };
    }
}
