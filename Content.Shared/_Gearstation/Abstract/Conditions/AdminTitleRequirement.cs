using Robust.Shared.Player;
using Content.Shared._Starlight.Abstract.Conditions;
using Content.Shared.Administration.Managers;

namespace Content.Shared._Gearstation.Abstract.Conditions;

/// <summary>
/// Requires the player to have one of the admin titles provided.
/// </summary>
public sealed partial class AdminTitleRequirement : BaseRequirement
{
    [Dependency] private ISharedAdminManager _adminManager = default!;

    private const string AnyTitles = "Any";

    [DataField(required: true)]
    public List<string> Titles = new();

    public override string GetRequirementDescription()
    {
        base.GetRequirementDescription();
        return Loc.GetString("requirements-title", ("titles",String.Join(", ",Titles)));
    }

    public override bool Handle(ICommonSession user)
    {
        base.Handle(user);

        var data = _adminManager.GetAdminData(user);
        if (data == null){ return false; }

        var title = data.Title;
        if (title == null) { return false; }

        return Titles.Contains(title) || Titles.Contains(AnyTitles);
    }
}
