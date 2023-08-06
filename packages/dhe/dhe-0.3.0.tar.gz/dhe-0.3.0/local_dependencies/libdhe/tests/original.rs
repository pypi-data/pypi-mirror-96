#![allow(non_snake_case)]
#![allow(dead_code)]
#![allow(unused_assignments)]
#![allow(non_upper_case_globals)]
#![allow(
    clippy::pedantic,
    clippy::style,
    clippy::eq_op,
    clippy::cognitive_complexity,
    clippy::manual_memcpy,
    clippy::float_cmp,
    clippy::unnecessary_operation
)]

use std::f64::consts::PI;
use std::f64::NAN;

pub const DIM_AXI_MAX: usize = 4;
pub const DIM_RAD_MAX: usize = 6;

pub const MAX_JAHRE: usize = 9;

pub const Def_Sicherheit1: usize = 4; // Zeitschritt Sole, Empfohlen: 4
pub const Def_Sicherheit2: usize = 2; // Zeitschritt Erde, Empfohlen: 2
pub const Def_DimRad: usize = 5; // Radiale Unterteilung, Max: 5
pub const Def_DimAxi: usize = 1; // Axiale Unterteilung, Max: 4
pub const Def_cpSole: f64 = 3875.; // Wasser: 4200 J/kgK
                                   // 33%Etylenglykol: 3800 J/kgK
pub const Def_cpFill: f64 = 3040.; // J/kgK
pub const Def_cpErde: f64 = 1000.; // J/kgK
pub const Def_rhoSole: f64 = 1050.; // kg/m3
pub const Def_rhoFill: f64 = 1180.; // kg/m3
pub const Def_rhoErde: f64 = 2600.; // kg/m3
pub const Def_lambdaSole: f64 = 0.449; // W/mK
pub const Def_lambdaFill: f64 = 0.81; // W/mK
pub const Def_lambdaErde: f64 = 2.0; // W/mK
pub const Def_nueSole: f64 = 0.00000415; // Wasser: 0.00000175 m2/s
                                         // 33%Ethylenglykol:ca0.000006 m2/s
pub const Def_RepRandbed: usize = 1; // Anzahl Wochen
pub const Def_Rechenradius: f64 = 1.5; // m
pub const Def_Gitterfaktor: f64 = 2.0; // Gitter in Erde, radial
pub const Def_AnzahlSonden: usize = 1; // Anzahl Sonden
pub const Def_Sondenlaenge: f64 = 100.; // m
pub const Def_Sondendurchmesser: f64 = 0.026; // m
pub const Def_Dicke_Sondenrohr: f64 = 0.000; // m
pub const Def_Bohrdurchmesser: f64 = 0.115; // m
pub const Def_R1: f64 = 0.0; // K/W, therm. Widerstand R1
pub const Def_Ra: f64 = 0.0; // Km/W, thermal pipe resistance Ra
pub const Def_Rb: f64 = 0.1; // Km/W, borhole thermal resistance
pub const Def_Massenstrom: f64 = 0.4; // kg/s, Solemassenstrom pro Sonde
pub const Def_TGrad: f64 = 0.03; // K/m, Temperaturgradient axial
pub const Def_Jahresmitteltemp: f64 = 9.0; // øC, Mittel Lufttemperatur
pub const Def_Bodenerwaermung: f64 = 0.8; // øC, Boden waermer als Luft
pub const Def_DeltaT: f64 = 0.0; // øC, Abkuehlung in der Waermepumpe
pub const Def_TSource: f64 = 0.0; // øC, Quellentemperatur
pub const Def_TSink: f64 = 4.0; // øC, Ruecklauftemp.(ohne Inputfile)
pub const Def_QSource: f64 = 5.0; // kW, Entzug (ohne Inputfile)
pub const Def_Zeitschritt: usize = 60; // Min
pub const Def_Simulationsdauer: usize = 8760; // h, totale Simulationszeit
pub const Def_readFile: bool = true;
pub const Def_writeFile: bool = true;
pub const Def_Allsteps: bool = false; // Auch Einschwingen aufschreiben
pub const Def_MonitorAxi: usize = 1;
pub const Def_MonitorRad: usize = 1;
pub const Def_Einschwingen: bool = false;
pub const Def_Leistungsinput: bool = false; // Entzugsleistung aus Inputfile
pub const Def_Leistung: bool = false; // Rechnen mit Entzugsleistung
pub const Def_stationaer: bool = false; // Stationaere Berechnung der Sole
pub const Def_Genauigkeit: f64 = 0.05; // øC, Iteration Leistungsberech.
pub const Def_Sprache: &str = "D";
pub const Def_StepWrite: usize = 1; // Ausgabeschritte: 2 fuer jede 2te
pub const Def_Jahr: usize = 1; // Beginn der Simulation
pub const Def_adiabat: f64 = 0.0; // Anteil adiabater Randbed. 0..1
pub const Def_Druck: bool = true; // Wird der Druckabfall berechnet?
pub const Def_g1: f64 = 4.82; // g-function bei ln(t/ts) = -4
pub const Def_g2: f64 = 5.69; // g-function bei ln(t/ts) = -2
pub const Def_g3: f64 = 6.29; // g-function bei ln(t/ts) = 0
pub const Def_g4: f64 = 6.57; // g-function bei ln(t/ts) = +2
pub const Def_g5: f64 = 6.60; // g-function bei ln(t/ts) = +3
pub const Def_gfunction: bool = true; // Randbedingung mit g-functions
pub const Def_Sondenabstand: f64 = 10.; // m, eff. Abstand der Sondenen
pub const Def_g_Sondenabstand: f64 = 10.; // m, Sondenabstand der g-function
pub const Def_Starttemp: bool = false; // Erdreichtemp. abschaetzen
pub const Def_LastYear: usize = 1; // Simulationsdauer in Jahren
pub const Def_AlteInputfiles: bool = false; // Alter, kurzer Eingabefilekopf
pub const Def_swewsInput: bool = false; // Liest Stoffwerte von SWEWS.DAT
pub const Def_Laufzeit_Jan: usize = 12; // h, taegliche Sondenlaufziet Jan
pub const Def_Laufzeit_Feb: usize = 11; // h, taegliche Sondenlaufziet Feb
pub const Def_Laufzeit_Mar: usize = 9; // h, taegliche Sondenlaufziet Mar
pub const Def_Laufzeit_Apr: usize = 7; // h, taegliche Sondenlaufziet Apr
pub const Def_Laufzeit_Mai: usize = 3; // h, taegliche Sondenlaufziet Mai
pub const Def_Laufzeit_Jun: usize = 2; // h, taegliche Sondenlaufziet Jun
pub const Def_Laufzeit_Jul: usize = 2; // h, taegliche Sondenlaufziet Jul
pub const Def_Laufzeit_Aug: usize = 2; // h, taegliche Sondenlaufziet Aug
pub const Def_Laufzeit_Sep: usize = 3; // h, taegliche Sondenlaufziet Sep
pub const Def_Laufzeit_Okt: usize = 7; // h, taegliche Sondenlaufziet Okt
pub const Def_Laufzeit_Nov: usize = 9; // h, taegliche Sondenlaufziet Nov
pub const Def_Laufzeit_Dez: usize = 11; // h, taegliche Sondenlaufziet Dez
pub const Def_QSpitzeFeb: usize = 5; // kW, Spitzenentzug im Februar
pub const Def_DauerLastspitze: usize = 4; // Tage, Dauer der Lastspitzen

pub type MatrixQ = [[f64; 53 * MAX_JAHRE]; DIM_AXI_MAX];
pub type Matrix = [[f64; DIM_RAD_MAX + 2]; DIM_AXI_MAX + 1];
pub type Vektor = [f64; DIM_AXI_MAX];
pub type VektorRad = [f64; DIM_RAD_MAX + 2];
pub type Vektor10 = [f64; 10];
pub type KMatrix = [[[f64; DIM_RAD_MAX + 1]; DIM_RAD_MAX + 1]; DIM_AXI_MAX];
pub type Matrix6 = [[f64; 7]; 7];

pub trait New {
    fn new() -> Self;
}

impl New for Vektor {
    fn new() -> Self {
        [NAN; DIM_AXI_MAX]
    }
}
impl New for VektorRad {
    fn new() -> Self {
        [NAN; DIM_RAD_MAX + 2]
    }
}
pub const Matrix_NAN: Matrix = [[NAN; DIM_RAD_MAX + 2]; DIM_AXI_MAX + 1];
impl New for Matrix {
    fn new() -> Self {
        Matrix_NAN
    }
}
impl New for KMatrix {
    fn new() -> Self {
        [[[NAN; DIM_RAD_MAX + 1]; DIM_RAD_MAX + 1]; DIM_AXI_MAX]
    }
}

pub fn multiplizieren(M: &KMatrix, w: &Matrix, y: &mut Matrix, k: usize, DimRad: usize) {
    /*    ***********    y = M x w       ************   */
    y[k][0] = w[k][0];
    y[k][DimRad + 1] = w[k][DimRad + 1];
    for i in 1..=DimRad {
        y[k][i] = 0.;
        for j in 0..=DimRad + 1 {
            if M[k][i][j] != M[k][i][j] {
                println!("M[{},{},{}]", k, i, j);
            }
            if w[k][j] != w[k][j] {
                println!("w[{},{}]", k, j);
            }
            y[k][i] = y[k][i] + M[k][i][j] * w[k][j];
        }
    }
}
fn WriteStep(
    _filestep: usize,
    _Massenstrom: f64,
    _TSink: f64,
    _QSource: f64,
    _TSource: f64,
    _TEarth: f64,
    _p: f64,
    _laminar: bool,
) {
}
fn ReadStep(_filestep: usize, _Massenstrom: f64, _TSink: f64, _QSource: f64) {}

pub fn TBRINE(
    T: Matrix,
    TDown: &mut [f64],
    TUp: &mut [f64],
    TSink: f64,
    L0: f64,
    L: &[f64],
    La: &[f64],
    Zeitschritt: usize,
    subdt: usize,
    substep: usize,
    QWand: &mut [f64],
    mcpSole: f64,
    mcpSoleUp: f64,
    mcpSoleDown: f64,
    DimAxi: usize,
    stationaer: bool,
    KoaxialSonde: bool,
) -> f64
// var i, k: integer
//    TOut, dt2, Lm0, Lm1, LmMin, L0mcpdt, Nichtad: float
{
    let mut SummeT: Vektor = [0.; DIM_AXI_MAX];
    let mut Td: Vektor = [0.; DIM_AXI_MAX];
    let mut Tu: Vektor = [0.; DIM_AXI_MAX];
    let mut dTa: Vektor = [0.; DIM_AXI_MAX];
    let dt2 = Zeitschritt as f64 * 60. / subdt as f64 / substep as f64; // [s]
    TDown[0] = TSink;
    let mut TOut: f64 = 0.;
    let L0mcpdt = L0 / mcpSole * dt2;
    for i in 1..DimAxi + 1 {
        SummeT[i] = 0.;
    }
    for _step in 1..substep + 1 {
        if KoaxialSonde {
            // KoaxialSonde: Neu 10.1.2000
            for i in 1..DimAxi + 1 {
                Td[i] = (T[i][1] - TDown[i]) * L[i] / mcpSoleDown * dt2;
                if stationaer {
                    TDown[i] = (L[i] * T[i][1] + L0 * TDown[i - 1] + La[i] * TUp[1 + DimAxi - i])
                        / (L[i] + L0 + La[i]);
                } else {
                    dTa[i] = TUp[1 + DimAxi - i] - TDown[i];
                    TDown[i] = TDown[i]
                        + (TDown[i - 1] - TDown[i]) * L0 / mcpSoleDown * dt2
                        + dTa[i] * La[i] / mcpSoleDown * dt2
                        + Td[i];
                }
                Td[i] = (T[i][1] - TDown[i]) * L[i] / mcpSoleDown * dt2;
            }
            TUp[0] = TDown[DimAxi];
            for i in 1..DimAxi + 1 {
                if stationaer {
                    TUp[i] = (La[1 + DimAxi - i] * TDown[1 + DimAxi - i] + L0 * TUp[i - 1])
                        / (La[1 + DimAxi - i] + L0);
                } else {
                    TUp[i] = TUp[i] + (TUp[i - 1] - TUp[i]) * L0 / mcpSoleUp * dt2
                        - dTa[1 + DimAxi - i] * La[1 + DimAxi - i] / mcpSoleUp * dt2;
                    // dTa[1 + DimAxi - 1] -> dTa[1 + DimAxi - i]
                }
            }
            for i in 1..DimAxi + 1 {
                SummeT[i] = SummeT[i] + Td[i];
            }
            TOut = TOut + TUp[DimAxi];
        // Koaxialsonde: # Ende des neuen Teils
        } else {
            // doppel - U - Sonde
            for i in 1..DimAxi + 1 {
                Td[i] = (T[i][1] - TDown[i]) * L[i] / 2. / mcpSole * dt2;
                if stationaer {
                    TDown[i] = (L[i] / 2. * T[i][1] + L0 * TDown[i - 1]) / (L[i] / 2. + L0);
                } else {
                    TDown[i] = TDown[i] + (TDown[i - 1] - TDown[i]) * L0mcpdt + Td[i];
                }
                Td[i] = (T[i][1] - TDown[i]) * L[i] / 2. / mcpSole * dt2;
            }

            TUp[0] = TDown[DimAxi];
            for i in 1..DimAxi + 1 {
                Tu[i] = (T[1 + DimAxi - i][1] - TUp[i]) * L[1 + DimAxi - i] / 2. / mcpSole * dt2;
                if stationaer {
                    TUp[i] = (L[1 + DimAxi - i] / 2. * T[1 + DimAxi - i][1] + L0 * TUp[i - 1])
                        / (L[1 + DimAxi - i] / 2. + L0);
                } else {
                    TUp[i] = TUp[i] + (TUp[i - 1] - TUp[i]) * L0mcpdt + Tu[i];
                }
                Tu[i] = (T[1 + DimAxi - i][1] - TUp[i]) * L[1 + DimAxi - i] / 2. / mcpSole * dt2;
            }
            for i in 1..DimAxi + 1 {
                SummeT[i] = SummeT[i] + Td[i] + Tu[1 + DimAxi - i];
            }
            TOut = TOut + TUp[DimAxi];
        } //(*** Ende Doppel - U - Sonde ** ***********************)
    }
    if KoaxialSonde {
        for i in 1..DimAxi + 1 {
            QWand[i] = SummeT[i] * mcpSoleDown;
        }
    } else {
        for i in 1..DimAxi + 1 {
            QWand[i] = SummeT[i] * mcpSole;
        }
    }
    TOut = TOut / substep as f64;
    return TOut;
}

//  Quellcode für die Berechnung der aeusseren Randbedingungen
pub fn RandAussen_gfunc(
    k: usize,
    Woche: usize,
    _Zeitschritt: usize,
    _simstep: usize,
    RepRandbed: usize,
    Q: MatrixQ,
    cpErd: f64,
    rhoErd: f64,
    lambdaErd: f64,
    Rechenradius: f64,
    Sondenlaenge: f64,
    gpar1: f64,
    gpar2: f64,
    gpar3: f64,
    gpar4: f64,
    gpar5: f64,
    gpar6: f64,
    DimAxi: usize,
    u_min: f64,
) -> f64 {
    /* Diese Funktion berechnet die Randbedingung mit der g-Function
     ************************************************************** */
    let mut u: f64;
    let mut STrt: f64;
    let ts: f64;
    let mut g: f64;
    let mut go: f64;
    let mut Rq: f64;

    ts = Sondenlaenge * Sondenlaenge / 9. / lambdaErd * rhoErd * cpErd;
    STrt = 0.;
    for i in 1..Woche + 1 {
        u = f64::ln(i as f64 / ts * (604800 * RepRandbed) as f64); // Aenderung 2.10.02
        if u > 2.5 {
            u = 2.5;
        }
        go = 0.5 * u + 6.84;
        if u < u_min {
            g = go;
        } else {
            g = gpar1
                + gpar2 * u
                + gpar3 * sqr(u)
                + gpar4 * u * sqr(u)
                + gpar5 * sqr(sqr(u))
                + gpar6 * u * sqr(sqr(u));
        }
        if u < -2. {
            if (go - 0.3) > g {
                g = go;
            }
        }
        g = g - f64::ln(Rechenradius / Sondenlaenge / 0.0005);
        Rq = g / 2. / PI / lambdaErd;
        STrt = STrt + (-Q[k][Woche - i + 1] + Q[k][Woche - i]) / Sondenlaenge * DimAxi as f64 * Rq;
    }
    return STrt;
}

pub fn RandAussen(
    k: usize,
    Woche: usize,
    _Zeitschritt: usize,
    _simstep: usize,
    RepRandbed: usize,
    Q: MatrixQ,
    cpErd: f64,
    rhoErd: f64,
    lambdaErd: f64,
    Rechenradius: f64,
    Sondenlaenge: f64,
    DimAxi: usize,
) -> f64 {
    /* Diese def berechnet die Randbedingung nach der Trichterformel
    von Werner ******************************************************** */
    let mut j: i64;
    let mut u: f64;
    let u0: f64;
    let mut W: f64;
    let mut W_alt: f64;
    let mut STrt: f64;
    let STrt0: f64;
    u0 = (Rechenradius) * (Rechenradius) * cpErd * rhoErd / (4. * lambdaErd);
    STrt0 = 4. * PI * lambdaErd * Sondenlaenge / DimAxi as f64;
    STrt = 0.;
    for i in 1..Woche + 1 {
        u = u0 / (i * 604800 * RepRandbed) as f64;
        if u > 1. {
            STrt = 0.;
        } else {
            W = -0.5772 - f64::ln(u);
            j = 1;
            W_alt = W - hoch(-1., j) * hoch(u, j) / (j * Fakultaet(j)) as f64;
            W = W_alt;
            loop {
                W_alt = W;
                j = j + 1;
                W = W - hoch(-1., j) / j as f64 * hoch(u, j) / (Fakultaet(j) as f64);
                if f64::abs(1. - W / W_alt) < 0.01 {
                    break;
                }
            }
            STrt = STrt + (-Q[k][Woche - i + 1] + Q[k][Woche - i]) / STrt0 * W;
        };
    }
    return STrt;
}

fn sqr(x: f64) -> f64 {
    return x * x;
}
fn hoch(a: f64, b: i64) -> f64 {
    // a^b
    if a > 0. {
        return f64::exp(b as f64 * f64::ln(a));
    } else {
        if b % 2 == 1 {
            return -f64::exp(b as f64 * f64::ln(-a));
        } else {
            return f64::exp(b as f64 * f64::ln(-a));
        }
    }
}
fn hoch_f(a: f64, b: f64) -> f64 {
    // a^b
    if a > 0. {
        return f64::exp(b as f64 * f64::ln(a));
    } else {
        panic!("a negative!");
    }
}
fn Fakultaet(x: i64) -> i64 {
    let mut y: i64;
    y = 1;
    for i in 1..=x {
        y = y * i;
    }
    return y;
}

pub type Gfunc = fn(
    usize,
    usize,
    usize,
    usize,
    usize,
    MatrixQ,
    f64,
    f64,
    f64,
    f64,
    f64,
    f64,
    f64,
    f64,
    f64,
    f64,
    f64,
    usize,
    f64,
) -> f64;

pub type GCone =
    fn(usize, usize, usize, usize, usize, MatrixQ, f64, f64, f64, f64, f64, usize) -> f64;

pub type FTbrine = fn(
    T: Matrix,
    &mut [f64],
    &mut [f64],
    f64,
    f64,
    &[f64],
    &[f64],
    usize,
    usize,
    usize,
    &mut [f64],
    f64,
    f64,
    f64,
    usize,
    bool,
    bool,
) -> f64;

pub fn calculateEWSGeneric(
    Iteration: i32,
    DimAxi: usize,
    DimRad: usize,
    MonitorAxi: usize,
    MonitorRad: usize,
    TEarthOld: &mut Matrix,
    TEarth: &mut Matrix,
    TUp: &mut Vektor,
    TUpOld: &mut Vektor,
    TDownOld: &mut Vektor,
    TDown: &mut Vektor,
    Q0Old: &mut Vektor,
    Q0: &mut Vektor,
    mut TSourceOld: f64,
    mut TSource: f64,
    mut TSourceMin: f64,
    mut TSourceMax: f64,
    mut TSink: f64,
    mut TSinkMin: f64,
    mut TSinkMax: f64,
    mut QSource: f64,
    Massenstrom: f64,
    cpSole: f64,
    p: f64,
    laminar: bool,
    readFile: bool,
    simstep: usize,
    StepWrite: usize,
    einschwingen: bool,
    Allsteps: bool,
    writeFile: bool,
    Leistung: bool,
    gfunction: bool,
    RepRandbed: usize,
    Zeitschritt: usize,
    Jahr: usize,
    numrows: usize,
    Starttemp: bool,
    DeltaT: f64,
    Subdt: usize,
    AnzahlSonden: usize,
    Rechenradius: f64,
    Stationaer: bool,
    mcpSole: f64,
    substep_run: usize,
    L1run: Vektor,
    substep_stop: usize,
    L1stop: Vektor,
    lambdaErde: Vektor10,
    rhoErde: Vektor10,
    cpErde: Vektor10,
    Q: &mut MatrixQ,
    T0: Vektor,
    B1: KMatrix,
    B2: KMatrix,
    Tneu: &mut Matrix,
    gpar6: f64,
    gpar5: f64,
    gpar4: f64,
    gpar3: f64,
    gpar2: f64,
    gpar1: f64,
    Sondenlaenge: f64,
    mut _TMonitor: f64,
    u_min: f64,
    TBRINE: FTbrine,
    RandAussen: GCone,
    RandAussen_gfunc: Gfunc,
) -> f64 {
    let mut filestep: usize = 0;
    let Woche: usize;
    let mut simstepn: usize;
    let mut Summe_TSource: f64;
    let L0: f64;
    let mut TRT: f64;
    let Pumpelauft: bool;
    let mut QWand: Vektor = [0.; DIM_AXI_MAX];
    {
        if Iteration == 0 {
            for i in 1..=DimAxi {
                for j in 1..=DimRad {
                    TEarthOld[i][j] = TEarth[i][j];
                }
                TUpOld[i] = TUp[i];
                TDownOld[i] = TDown[i];
                Q0Old[i] = Q0[i];
            }
        } else {
            for i in 1..=DimAxi {
                for j in 1..=DimRad {
                    TEarth[i][j] = TEarthOld[i][j];
                }
                TUp[i] = TUpOld[i];
                TDown[i] = TDownOld[i];
                Q0[i] = Q0Old[i];
            }
        }

        if Iteration == 0 {
            if !readFile {
                filestep = simstep - 1;
            }
            if simstep > 1 {
                if !einschwingen || Allsteps {
                    if TSource < TSourceMin {
                        TSourceMin = TSource;
                    }
                    if TSource > TSourceMax {
                        TSourceMax = TSource;
                    }
                    if TSink < TSinkMin {
                        TSinkMin = TSink;
                    }
                    if TSink > TSinkMax {
                        TSinkMax = TSink;
                    }
                    if writeFile {
                        if ((simstep - 1) % StepWrite) == 0 {
                            if Leistung {
                                if Massenstrom > 0.0001 {
                                    TSink = TSource - QSource * 1000. / Massenstrom / cpSole;
                                } else {
                                    TSink = TSource;
                                }
                            } else {
                                QSource = (TSource - TSink) * Massenstrom * cpSole / 1000.;
                            }
                            WriteStep(
                                filestep,
                                Massenstrom,
                                TSink,
                                QSource,
                                TSource,
                                TEarth[MonitorAxi][MonitorRad],
                                p,
                                laminar,
                            );
                        }
                    }
                }
            }
            if readFile {
                ReadStep(filestep, Massenstrom, TSink, QSource);
            }
            if DeltaT != 0. {
                TSink = TSourceOld - DeltaT;
            }
        }

        if Iteration > -1 {
            Summe_TSource = 0.;
            if !Starttemp {
                Woche =
                    (simstep + numrows * (Jahr - 1) - 1) / (10080 / Zeitschritt * RepRandbed) + 1;
                simstepn = (simstep + numrows * (Jahr - 1)) % (10080 / Zeitschritt * RepRandbed);
            } else {
                Woche = (simstep - 1) / (10080 / Zeitschritt * RepRandbed) + 1;
                simstepn = (simstep) % (10080 / Zeitschritt * RepRandbed);
            };
            if simstepn == 0 {
                simstepn = 10080 / RepRandbed / Zeitschritt;
            }
            // Rechengebiet = Rechenradius - Bohrdurchmesser / 2;
            L0 = cpSole * Massenstrom / AnzahlSonden as f64;
            if Massenstrom > 0.00001 {
                Pumpelauft = true;
            } else {
                Pumpelauft = false;
            }
            for idt in 1..=Subdt {
                //  calculate brine Temperature
                if Pumpelauft {
                    TSource = TBRINE(
                        *TEarth,
                        TDown,
                        TUp,
                        TSink,
                        L0,
                        &L1run,
                        &[0.], /*La*/
                        Zeitschritt,
                        Subdt,
                        substep_run,
                        &mut QWand,
                        mcpSole,
                        0., /*mcpSoleUp*/
                        0., /*mcpSoleDown*/
                        DimAxi,
                        Stationaer,
                        false, /*KoaxialSonde*/
                    );
                    for i in 1..=DimAxi {
                        TEarth[i][0] = TEarth[i][1]
                            - QWand[i] / L1run[i] / Zeitschritt as f64 / 60. * Subdt as f64;
                    }
                } else {
                    TSource = TBRINE(
                        *TEarth,
                        TDown,
                        TUp,
                        0.,
                        0.,
                        &L1stop,
                        &[0.], /*La*/
                        Zeitschritt,
                        Subdt,
                        substep_stop,
                        &mut QWand,
                        mcpSole,
                        0., /*mcpSoleUp*/
                        0., /*mcpSoleDown*/
                        DimAxi,
                        Stationaer,
                        false, /*KoaxialSonde*/
                    );
                    for i in 1..=DimAxi {
                        TEarth[i][0] = TEarth[i][1]
                            - QWand[i] / L1stop[i] / Zeitschritt as f64 / 60. * Subdt as f64;
                    }
                }
                for i in 1..=DimAxi {
                    //  calculate temperature at outer boudary condition at each RepRandBed
                    Q0[i] = (Q0[i] * (((simstepn - 1) * Subdt) as f64 + (idt - 1) as f64)
                        + QWand[i] * Subdt as f64 / Zeitschritt as f64 / 60.)
                        / ((simstepn - 1) * Subdt + idt) as f64;
                    if Iteration == 0 {
                        if idt == Subdt {
                            if ((simstep + numrows * (Jahr - 1)) * Zeitschritt)
                                % (60 * 24 * 7 * RepRandbed)
                                == 0
                            {
                                Q[i][Woche] = Q0[i];
                                if gfunction {
                                    TRT = RandAussen_gfunc(
                                        i,
                                        Woche,
                                        Zeitschritt,
                                        simstep + numrows * (Jahr - 1),
                                        RepRandbed,
                                        *Q,
                                        cpErde[i],
                                        rhoErde[i],
                                        lambdaErde[i],
                                        Rechenradius,
                                        Sondenlaenge,
                                        gpar1,
                                        gpar2,
                                        gpar3,
                                        gpar4,
                                        gpar5,
                                        gpar6,
                                        DimAxi,
                                        u_min,
                                    );
                                } else {
                                    TRT = RandAussen(
                                        i,
                                        Woche,
                                        Zeitschritt,
                                        simstep + numrows * (Jahr - 1),
                                        RepRandbed,
                                        *Q,
                                        cpErde[i],
                                        rhoErde[i],
                                        lambdaErde[i],
                                        Rechenradius,
                                        Sondenlaenge,
                                        DimAxi,
                                    );
                                }
                                TEarth[i][DimRad + 1] = T0[i] + TRT;
                            };
                        };
                    };
                    //  calulate earth temperature
                    if Pumpelauft {
                        multiplizieren(&B1, &TEarth, Tneu, i, DimRad);
                    } else {
                        multiplizieren(&B2, &TEarth, Tneu, i, DimRad);
                    }
                    for j in 1..=DimRad {
                        TEarth[i][j] = Tneu[i][j];
                    }
                }
                Summe_TSource = Summe_TSource + TSource;
            }
            TSource = Summe_TSource / Subdt as f64; //  avarage source temperature
            TSourceOld = TSource;
            _TMonitor = TEarth[MonitorAxi][MonitorRad];
        }
    }
    return TSource;
}

pub fn calculateEWS(
    Iteration: i32,
    DimAxi: usize,
    DimRad: usize,
    MonitorAxi: usize,
    MonitorRad: usize,
    TEarthOld: &mut Matrix,
    TEarth: &mut Matrix,
    TUp: &mut Vektor,
    TUpOld: &mut Vektor,
    TDownOld: &mut Vektor,
    TDown: &mut Vektor,
    Q0Old: &mut Vektor,
    Q0: &mut Vektor,
    TSourceOld: f64,
    TSource: f64,
    TSourceMin: f64,
    TSourceMax: f64,
    TSink: f64,
    TSinkMin: f64,
    TSinkMax: f64,
    QSource: f64,
    Massenstrom: f64,
    cpSole: f64,
    p: f64,
    laminar: bool,
    readFile: bool,
    simstep: usize,
    StepWrite: usize,
    einschwingen: bool,
    Allsteps: bool,
    writeFile: bool,
    Leistung: bool,
    gfunction: bool,
    RepRandbed: usize,
    Zeitschritt: usize,
    Jahr: usize,
    numrows: usize,
    Starttemp: bool,
    DeltaT: f64,
    Subdt: usize,
    AnzahlSonden: usize,
    Rechenradius: f64,
    Stationaer: bool,
    mcpSole: f64,
    substep_run: usize,
    L1run: Vektor,
    substep_stop: usize,
    L1stop: Vektor,
    lambdaErde: Vektor10,
    rhoErde: Vektor10,
    cpErde: Vektor10,
    Q: &mut MatrixQ,
    T0: Vektor,
    B1: KMatrix,
    B2: KMatrix,
    Tneu: &mut Matrix,
    gpar6: f64,
    gpar5: f64,
    gpar4: f64,
    gpar3: f64,
    gpar2: f64,
    gpar1: f64,
    Sondenlaenge: f64,
    mut _TMonitor: f64,
    u_min: f64,
) -> f64 {
    calculateEWSGeneric(
        Iteration,
        DimAxi,
        DimRad,
        MonitorAxi,
        MonitorRad,
        TEarthOld,
        TEarth,
        TUp,
        TUpOld,
        TDownOld,
        TDown,
        Q0Old,
        Q0,
        TSourceOld,
        TSource,
        TSourceMin,
        TSourceMax,
        TSink,
        TSinkMin,
        TSinkMax,
        QSource,
        Massenstrom,
        cpSole,
        p,
        laminar,
        readFile,
        simstep,
        StepWrite,
        einschwingen,
        Allsteps,
        writeFile,
        Leistung,
        gfunction,
        RepRandbed,
        Zeitschritt,
        Jahr,
        numrows,
        Starttemp,
        DeltaT,
        Subdt,
        AnzahlSonden,
        Rechenradius,
        Stationaer,
        mcpSole,
        substep_run,
        L1run,
        substep_stop,
        L1stop,
        lambdaErde,
        rhoErde,
        cpErde,
        Q,
        T0,
        B1,
        B2,
        Tneu,
        gpar6,
        gpar5,
        gpar4,
        gpar3,
        gpar2,
        gpar1,
        Sondenlaenge,
        _TMonitor,
        u_min,
        TBRINE,
        RandAussen,
        RandAussen_gfunc,
    )
}

pub fn Polynom(
    g1: f64,
    g2: f64,
    g3: f64,
    g4: f64,
    g5: f64,
    Sondenabstand: f64,
    g_Sondenabstand: f64,
) -> (f64, [f64; 6]) {
    // var
    //    pivot,BH,g10,g20,g30,g40,g50,ExA,ExB : float
    //    g,i,j                                  : int

    let mut x: Vektor10 = [0.; 10];
    let mut y: Vektor10 = [0.; 10];
    let mut w: Vektor10 = [0.; 10];
    let mut A: Matrix6 = [[0.; 7]; 7];
    let mut Ainv: Matrix6 = [[0.; 7]; 7];
    let mut _ErrorMldg;

    let mut g10 = g1;
    let mut g20 = g2;
    let mut g30 = g3;
    let mut g40 = g4;
    let mut g50 = g5;
    let mut uMin;
    let mut pivot;
    if f64::abs(Sondenabstand - g_Sondenabstand) > 0.05 {
        //  Extrapolation der g-Function
        let BH = Sondenabstand / g_Sondenabstand;
        if BH < 0.4 {
            _ErrorMldg = 1;
        }
        uMin = -4.;
        let ExA = g5 - 6.29;
        let ExB = -f64::ln((g3 - 6.29) / (g5 - 6.6)) / 27.;
        g10 = Max(4.82 + ExA / BH * f64::exp(-BH * ExB * 343.), 4.82);
        if f64::abs(g10 - 4.82) < 1.5 {
            g10 = 4.82;
        } else {
            g10 = (g10 + 4.82) / 2.;
        }
        g20 = Max(5.69 + ExA / BH * f64::exp(-BH * ExB * 125.), 5.69);
        g30 = Max(6.29 + ExA / BH * f64::exp(-BH * ExB * 27.), 6.29);
        g40 = Max(6.57 + ExA / BH * f64::exp(-BH * ExB), 6.57);
        g50 = Max(6.6 + ExA / BH, 6.6);
        // e Extrapolation g-Function
    }
    // Berechnet die g-function aus 4 Stuetztstellen g1,g2,g3,g4
    x[1] = -4.;
    x[2] = -2.;
    x[3] = 0.;
    x[4] = 2.5;
    x[5] = 3.;
    x[6] = f64::min(-4.5, -4. - (g10 - 4.82) / 2.);
    uMin = f64::max(x[6] + 0.5, -6.);
    y[1] = g10;
    y[2] = g20;
    y[3] = g30;
    y[4] = g40;
    y[5] = g50 * 0.99;
    y[6] = (f64::ln(0.5 / 0.0005) + 0.5 * x[6]) * 0.95;
    y[4] = (y[4] + y[5]) / 2. * 0.99;
    for i in 1..=6 {
        A[i][1] = 1.;
        for j in 2..=6 {
            A[i][j] = A[i][j - 1] * x[i];
        }
    }

    // invertiert die 6 x 6 Matrix A nach der Diagonalen-Methode
    for i in 1..=6 {
        for j in 1..=6 {
            Ainv[i][j] = A[i][j];
        }
    }
    for g in 1..=6 {
        pivot = Ainv[g][g];
        for j in 1..=6 {
            Ainv[g][j] = Ainv[g][j] * (-1.) / pivot;
        }
        for i in 1..=6 {
            for j in 1..=6 {
                if i != g && j != g {
                    Ainv[i][j] = Ainv[g][j] * Ainv[i][g] + Ainv[i][j];
                }
            }
            Ainv[i][g] = Ainv[i][g] / pivot;
        }

        Ainv[g][g] = 1. / pivot;
        // e invertieren
        // w = Ainv * y
    }
    for i in 1..=6 {
        w[i] = 0.;
    }
    for i in 1..=6 {
        for j in 1..=6 {
            w[i] = w[i] + Ainv[i][j] * y[j];
        }
    }
    let mut w_out = [0.; 6];
    &w_out.clone_from_slice(&w[1..7]);
    return (uMin, w_out);
}

fn Max(x1: f64, x2: f64) -> f64 {
    if x1 > x2 {
        return x1;
    } else {
        return x2;
    }
}

pub fn r_grid(
    Sondendurchmesser: f64,
    Bohrdurchmesser: f64,
    Rechengebiet: f64,
    Gitterfaktor: f64,
    DimRad: usize,
) -> VektorRad {
    let mut r: VektorRad = [0.; DIM_RAD_MAX + 2];
    r[0] = Sondendurchmesser / 2.;
    r[1] = Bohrdurchmesser / 2.;
    let Faktor = Rechengebiet * (1. - Gitterfaktor) / (1. - hoch(Gitterfaktor, DimRad as i64 - 1));
    for i in 2..=DimRad {
        r[i] = r[i - 1] + Faktor * hoch(Gitterfaktor, i as i64 - 2);
    }
    return r;
}

pub fn rz_grid(r: &VektorRad, DimRad: usize) -> VektorRad {
    let mut rz: VektorRad = [0.; DIM_RAD_MAX + 2];
    for i in 1..=DimRad {
        rz[i] = f64::sqrt((r[i] * r[i] + r[i - 1] * r[i - 1]) / 2.);
    }
    rz[0] = r[0];
    rz[DimRad + 1] = r[DimRad];
    return rz;
}

pub fn alpha1(
    NueSole: f64,
    rhoSole: f64,
    cpSole: f64,
    lambdaSole: f64,
    Massenstrom: f64,
    Sondurchmesser: f64,
    Dicke_Sondenrohr: f64,
) -> f64 {
    //  Function alpha1: Waermeuebergang Sole-Hinterfuellung, wenn Pumpe laeuft
    // var x,Geschw,Re,Pr,Nu_turbulent,Nu_laminar,
    //    Nu0,Nu,Di,St,Xi0,Xi,K1,K2,K10,St0       : float

    let Di = Sondurchmesser - 2. * Dicke_Sondenrohr;
    let Geschw = 2. * Massenstrom / rhoSole / Di.powi(2) / PI;
    let Re = Geschw * Di / NueSole; // Reynoldszahl
    let Pr = NueSole * rhoSole * cpSole / lambdaSole; // Prandtlzahl
                                                      //  Xi = Druckverlustkoeffizient nach Petukhov (1970)
    let Xi = 1. / 1.82 * f64::ln(Re.powi(2) / f64::ln(10.) - 1.64);
    //  Stantonzahl nach Petukhov (1970), gueltig fuer turbulenten Bereich
    let K1 = 1. + 27.2 * Xi / 8.;
    let K2 = 11.7 + 1.8 / hoch_f(Pr, 1. / 3.);
    let St = Xi / 8. / (K1 + K2 * f64::sqrt(Xi / 8.) * (hoch_f(Pr, 2. / 3.) - 1.)); // Stantonzahl
                                                                                    // Stantonzahl nach Petukhov an der Grenze turbulent-Uebergangszone
    let Xi0 = 0.031437;
    let K10 = 1.106886;
    let ST0 = Xi0 / 8. / (K10 + K2 * f64::sqrt(Xi0 / 8.) * (hoch_f(Pr, 2. / 3.) - 1.));
    let Nu0 = ST0 * 10000. * Pr; // Nusseltzahl beim Uebergang turbulent-Uebergangszone
    let Nu_turbulent = St * Re * Pr; // Nusseltzahl turbulente Zone
    let Nu_laminar = 4.36; // Nusseltzahl laminare Zone
    let mut Nu = NAN;
    if Re >= 10000. {
        Nu = Nu_turbulent;
    } // turbulent
    if Re <= 2300. {
        Nu = Nu_laminar;
    }
    // laminar
    // Uebergangszone laminar/turbulent
    else {
        if Re < 10000. {
            Nu = Nu_laminar
                * f64::exp(
                    f64::ln(Nu0 / Nu_laminar) / f64::ln(10000. / 2300.) * f64::ln(Re / 2300.),
                );
        }
    }
    let x = Nu * lambdaSole / Di;
    return x;
}

/* resistances(
            DimAxi, 0., dl, &r, &rz, alpha, &lambdaErde, *Ra, *Rb,
            Def_lambdaFill,
            Def_lambdaSole,
            Def_Sondendurchmesser);
*/
pub fn resistances(
    DimAxi: usize,
    mut R1: f64,
    dl: f64,
    r: &[f64],
    rz: &[f64],
    alpha: f64,
    lambdaErde: &[f64],
    lambdaSole: f64,
    lambdaFill: f64,
    mut Ra: f64,
    mut Rb: f64,
    Sondendurchmesser: f64,
) -> (f64, f64, f64, Vektor) {
    let mut R2 = Vektor::new();
    let mut L1run = NAN;
    let mut L1stop = NAN;
    if Ra > 0. && Rb > 0. {
        R1 = Ra / 4. / dl;
        println!(
            "(Ra > 0) and (Rb > 0) ---> Ra = {}, dl = {}, {}",
            Ra, dl, R1
        );
        for i in 1..=DimAxi {
            R2[i] = (Rb - Ra / 4.) / dl + 1. / 2. / PI / dl * f64::ln(rz[2] / r[1]) / lambdaErde[i];
        }
        L1run = 1. / R1;
        L1stop = 1.
            / (R1 - 1. / 8. / PI / alpha / r[0] / dl
                + 1. / 8. / PI / alpha0(lambdaSole, Sondendurchmesser) / r[0] / dl);
    } else if Rb > 0. {
        println!("Rb > 0");
        R1 = Rb / dl - 1. / 2. / PI / dl * f64::ln(r[1] / rz[1]) / lambdaFill;
        for i in 1..=DimAxi {
            R2[i] = 1. / 2. / PI / dl
                * (f64::ln(r[1] / rz[1]) / lambdaFill + f64::ln(rz[2] / r[1]) / lambdaErde[i]);
        }
        L1run = 1. / R1;
        L1stop = 1.
            / (R1 - 1. / 8. / PI / alpha / r[0] / dl
                + 1. / 8. / PI / alpha0(lambdaSole, Sondendurchmesser) / r[0] / dl);
        Ra = R1 * 4. * dl;
    } else if R1 > 0. {
        println!("R1 > 0.");
        for i in 1..=DimAxi {
            R2[i] = 1. / 2. / PI / dl
                * (f64::ln(r[1] / rz[1]) / lambdaFill + f64::ln(rz[2] / r[1]) / lambdaErde[i]);
        }
        L1run = 1. / R1;
        L1stop = 1.
            / (R1 - 1. / 8. / PI / alpha / r[0] / dl
                + 1. / 8. / PI / alpha0(lambdaSole, Sondendurchmesser) / r[0] / dl);
        Ra = R1 * 4. * dl;
        Rb = R1 * dl + 1. / 2. / PI * f64::ln(r[1] / rz[1]) / lambdaFill;
    } else {
        println!("else");
        R1 = 1. / 8. / PI / dl * (1. / alpha / r[0] + f64::ln((r[1] - rz[1]) / r[0]) / lambdaFill);
        for i in 1..=DimAxi {
            R2[i] = 1. / 2. / PI / dl
                * (f64::ln(r[1] / rz[1]) / lambdaFill + f64::ln(rz[2] / r[1]) / lambdaErde[i]);
        }
        L1run = 1. / R1;
        L1stop = 8.
            / (1. / PI / alpha0(lambdaSole, Sondendurchmesser) / r[0] / dl
                + f64::ln((r[1] - rz[1]) / r[0]) / PI / lambdaFill / dl);
        Ra = R1 * 4. * dl;
        Rb = R1 * dl + 1. / 2. / PI * f64::ln(r[1] / rz[1]) / lambdaFill;
    }
    return (L1run, L1stop, R1, R2);
}

/// Waermeuebergang, wenn Pumpe steht
fn alpha0(lambdaSole: f64, Sondurchmesser: f64) -> f64 {
    return lambdaSole / (Sondurchmesser / 2. * (1. - f64::sqrt(0.5)));
}

pub fn C_matrix(
    DimAxi: usize,
    DimRad: usize,
    r: &[f64],
    dl: f64,
    cpErde: &[f64],
    rhoErde: &[f64],
    cpFill: f64,
    rhoFill: f64,
) -> Matrix {
    let mut C = Matrix::new();
    for i in 1..=DimAxi {
        C[i][1] = cpFill * rhoFill * PI * (r[1] * r[1] - 4. * r[0] * r[0]) * dl;
        for j in 2..=DimRad {
            C[i][j] = cpErde[i] * rhoErde[i] * PI * (r[j] * r[j] - r[j - 1] * r[j - 1]) * dl;
        }
    }
    return C;
}

pub fn L1run_matrix(
    DimAxi: usize,
    DimRad: usize,
    L1run: f64,
    L1stop: f64,
    R2: &[f64],
    lambdaErde: &[f64],
    r: &[f64],
    rz: &[f64],
    dl: f64,
    adiabat: f64,
) -> (Matrix, Matrix) {
    let mut L1 = Matrix::new();
    let mut L2 = Matrix::new();
    let mut Llast = Vektor::new();
    for i in 1..=DimAxi {
        L1[i][1] = L1run;
        L1[i][2] = 1. / R2[i];
        for j in 3..=DimRad {
            L1[i][j] = 1. / (f64::ln(rz[j] / rz[j - 1]) / 2. / PI / lambdaErde[i] / dl);
        }
        Llast[i] =
            (1. - adiabat) / (1. / 2. / PI / dl / lambdaErde[i] * f64::ln(r[DimRad] / rz[DimRad]));
        L1[i][DimRad + 1] = Llast[i];
    }
    for i in 1..=DimAxi {
        L2[i][1] = L1stop;
        for j in 2..=DimRad + 1 {
            L2[i][j] = L1[i][j];
        }
    }
    return (L1, L2);
}

pub fn Optimaler_Zeitfaktor(
    DimAxi: usize,
    Zeitschritt: usize,
    L: Matrix,
    C: Matrix,
    stationaer: bool,
    Sicherheit2: f64,
) -> usize {
    // var i,Optfak                 : int
    //     Mindx,Mindt,Mindt2       : float

    let mut Mindt = 3600.;
    for i in 1..=DimAxi {
        let mut Mindt2 = C[i][1] / L[i][2] / Sicherheit2;
        if Mindt2 < Mindt {
            Mindt = Mindt2;
        }
        Mindt2 = C[i][2] / L[i][2] / Sicherheit2;
        if Mindt2 < Mindt {
            Mindt = Mindt2;
        }
        if !stationaer {
            Mindt2 = C[i][1] / L[i][1] / Sicherheit2;
        } else {
            Mindt2 = C[i][1] / L[i][1] / Sicherheit2 * 1.0;
        }
        if Mindt2 < Mindt {
            Mindt = Mindt2;
        }
    }
    let mut Optfak = (Zeitschritt as f64 * 60. / Mindt) as usize;
    if Optfak == 0 {
        Optfak = 1;
    }
    return Optfak;
}

/// Anfangstemp:    Ungestoerte Erde
pub fn Anfangstemp(
    TMittel: f64,
    TGrad: f64,
    dl: f64,
    qEntzug: Vektor,
    TEarth: &mut Matrix,
    T0: &mut Vektor,
    TUp: &mut Vektor,
    TUpold: &mut Vektor,
    TDown: &mut Vektor,
    TDownOld: &mut Vektor,
    _TSource: f64,
    DimAxi: usize,
    DimRad: usize,
    StartJahr: usize,
    gpar1: f64,
    gpar2: f64,
    gpar3: f64,
    gpar4: f64,
    gpar5: f64,
    gpar6: f64,
    lambdaErd: f64,
    rhoErd: f64,
    cpErd: f64,
    uMin: f64,
    rz: &[f64],
    Sondenlaenge: f64,
) {
    // var i,j      : integer;
    // ts,u     : real;
    // go,g1    : real;
    let mut g = VektorRad::new();
    let mut Rq = VektorRad::new();
    let ts = (dl * DimAxi as f64) * (dl * DimAxi as f64) / 9. / lambdaErd * rhoErd * cpErd;
    let mut u;
    if StartJahr > 0 {
        u = f64::ln(StartJahr as f64 * 365.) + f64::ln(24. * 3600.) - f64::ln(ts);
    } else {
        u = 0.;
    }
    if u > 2.5 {
        u = 2.5;
    }
    let go = 0.5 * u + 6.907755;
    let mut g1;
    if u < uMin {
        g1 = go;
    } else {
        g1 = gpar1
            + gpar2 * u
            + gpar3 * u.powi(2)
            + gpar4 * u.powi(3)
            + gpar5 * u.powi(4)
            + gpar6 * u.powi(5);
    }
    if u < -2. {
        if (go - 0.3) > g1 {
            g1 = go;
        }
    }
    for j in 0..=DimRad + 1 {
        g[j] = g1 - f64::ln(rz[j] / dl / DimAxi as f64 / 0.0005);
        if StartJahr == 0 {
            Rq[j] = 0.;
        } else {
            Rq[j] = g[j] / 2. / PI / lambdaErd;
        }
    }
    for i in 1..=DimAxi {
        for j in 0..=DimRad + 1 {
            TEarth[i][j] = TMittel + (i as f64 * dl - dl / 2.) * TGrad
                - qEntzug[i] / Sondenlaenge * DimAxi as f64 * Rq[j];
        }
        T0[i] = TEarth[i][DimRad + 1];
        TUp[DimAxi - i + 1] = TEarth[i][0];
        TUpold[DimAxi - i + 1] = TEarth[i][0];
        TDown[i] = TEarth[i][0];
        TDownOld[i] = TEarth[i][0];
    }
}

///  ***********     B = Ainv x F *****
pub fn _B(L: &Matrix, C: &Matrix, dt: f64, DimAxi: usize, DimRad: usize) -> KMatrix {
    fn MultiMatrix(Ainv: &KMatrix, F: &KMatrix, B: &mut KMatrix, DimAxi: usize, DimRad: usize) {
        // var i,j,k,l      : int

        for l in 1..=DimAxi {
            for k in 0..=DimRad + 1 {
                for i in 0..=DimRad + 1 {
                    B[l][k][i] = 0.;
                    for j in 0..=DimRad + 1 {
                        B[l][k][i] = B[l][k][i] + Ainv[l][k][j] * F[l][j][i];
                    }
                }
            }
        }
    }
    /// Diese Procedure invertiert die n x n Matrix A nach der Diagonalen-Methode,
    ///    **************     Ainv = 1/A und n = DimRad+1 ***************************
    fn invertieren(A: &KMatrix, Ainv: &mut KMatrix, DimAxi: usize, DimRad: usize) {
        // var
        //  pivot      : float
        //  g,i,j,k    : int
        for k in 1..=DimAxi {
            for i in 0..=DimRad + 1 {
                for j in 0..=DimRad + 1 {
                    Ainv[k][i][j] = A[k][i][j];
                }
            }
            for g in 0..=DimRad + 1 {
                let pivot = Ainv[k][g][g];
                for j in 0..=DimRad + 1 {
                    Ainv[k][g][j] = Ainv[k][g][j] * (-1.) / pivot;
                }
                for i in 0..=DimRad + 1 {
                    for j in 0..=DimRad + 1 {
                        if (i != g) && (j != g) {
                            Ainv[k][i][j] = Ainv[k][g][j] * Ainv[k][i][g] + Ainv[k][i][j];
                        }
                    }
                    Ainv[k][i][g] = Ainv[k][i][g] / pivot;
                }
                Ainv[k][g][g] = 1. / pivot;
            }
        }
    }
    fn DefMatrixA(L: &Matrix, C: &Matrix, dt: f64, A: &mut KMatrix, DimAxi: usize, DimRad: usize) {
        // var i,j,k : int

        for i in 1..=DimAxi {
            for j in 0..=DimRad + 1 {
                for k in 0..=DimRad + 1 {
                    A[i][j][k] = 0.;
                }
            }
            A[i][0][0] = 1.;
            A[i][DimRad + 1][DimRad + 1] = 1.;
            for j in 1..=DimRad {
                A[i][j][j] = 2. * C[i][j] + dt * (L[i][j] + L[i][j + 1]);
                A[i][j][j - 1] = -dt * L[i][j];
                A[i][j][j + 1] = -dt * L[i][j + 1];
            }
        }
    }

    fn DefMatrixF(L: &Matrix, C: &Matrix, dt: f64, F: &mut KMatrix, DimAxi: usize, DimRad: usize) {
        // var i,j,k : int
        for i in 1..=DimAxi {
            for j in 0..=DimRad + 1 {
                for k in 0..=DimRad + 1 {
                    F[i][j][k] = 0.;
                }
            }
            F[i][0][0] = 1.;
            F[i][DimRad + 1][DimRad + 1] = 1.;
            for j in 1..=DimRad {
                F[i][j][j] = 2. * C[i][j] - dt * (L[i][j] + L[i][j + 1]);
                F[i][j][j - 1] = dt * L[i][j];
                F[i][j][j + 1] = dt * L[i][j + 1];
            }
        }
    }
    //  Definition der Matrizen, wobei A * Tneu = F * Talt
    let mut A1 = KMatrix::new();
    let mut Ainv1 = KMatrix::new();
    let mut F1 = KMatrix::new();
    let mut B1 = KMatrix::new();
    DefMatrixA(L, C, dt, &mut A1, DimAxi, DimRad); // Pumpe laeuft
    DefMatrixF(L, C, dt, &mut F1, DimAxi, DimRad);
    invertieren(&A1, &mut Ainv1, DimAxi, DimRad);
    MultiMatrix(&Ainv1, &F1, &mut B1, DimAxi, DimRad);

    return B1;
}
