using Robust.Shared;
using Robust.Shared.Configuration;

namespace Content.Shared._Gearstation.CCVar;

[CVarDefs]
public sealed class GearCCVars
{
    /// <summary>
    ///     How many times players can vote to not evac before an unrecallable shuttle is called.
    /// </summary>
    public static readonly CVarDef<int> MaxAutoEvacRefuseMax =
        CVarDef.Create("gear.auto_evac_refuse_max", 2, CVar.SERVERONLY);

}
