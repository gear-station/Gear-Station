using Robust.Shared;
using Robust.Shared.Configuration;

namespace Content.Shared._Gearstation.CCVar;

[CVarDefs]
public sealed class GearCCVars
{
    /// <summary>
    ///     Option to lower the severity of muffling when in space.
    /// </summary>
    public static readonly CVarDef<float> VacuumHearingMultiplier =
        CVarDef.Create("audio.vacuum_hearing_multiplier", 1f, CVar.CLIENTONLY | CVar.ARCHIVE);

}
