#![allow(non_snake_case)]
#![allow(dead_code)]
#![allow(clippy::manual_memcpy)]

use std::f64::NAN;

use libdhe::{self, BoundaryMethod, TBrineMethod};
mod assert_arr;
mod original;
use assert_arr::EPS;
use original::{
    calculateEWSGeneric, Def_AnzahlSonden, Def_DeltaT, Def_Massenstrom, Def_QSource,
    Def_Rechenradius, Def_RepRandbed, Def_Sicherheit1, Def_Simulationsdauer, Def_Sondenlaenge,
    Def_Zeitschritt, Def_cpSole, Def_lambdaErde, KMatrix, Matrix, MatrixQ, New, Vektor10,
    MAX_JAHRE,
};
mod shared;
use shared::Delta_T_boundary_1;

const DIM_AXI: usize = 3;
const DIM_RAD: usize = 5;
const DIM_T: usize = 10;

const SIZE_AXI: usize = DIM_AXI + 1;

struct PasConfig {
    Iteration: i32,
    DimAxi: usize,
    DimRad_: usize,
    MonitorAxi: usize,
    MonitorRad: usize,
    TEarthOld: Matrix,
    TEarth: Matrix,
    TUp: [f64; DIM_AXI + 1],
    TUpOld: [f64; DIM_AXI + 1],
    TDownOld: [f64; DIM_AXI + 1],
    TDown: [f64; DIM_AXI + 1],
    Q0Old: [f64; DIM_AXI + 1],
    Q0: [f64; DIM_AXI + 1],
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
    subdt: usize,
    AnzahlSonden: usize,
    Rechenradius: f64,
    Stationaer: bool,
    mcpSole: f64,
    substep_run: usize,
    L1run: [f64; DIM_AXI + 1],
    substep_stop: usize,
    L1stop: [f64; DIM_AXI + 1],
    lambdaErde: Vektor10,
    rhoErde: Vektor10,
    cpErde: Vektor10,
    Q: MatrixQ,
    T0: [f64; DIM_AXI + 1],
    B1: KMatrix,
    B2: KMatrix,
    Tneu: Matrix,
    gpar6: f64,
    gpar5: f64,
    gpar4: f64,
    gpar3: f64,
    gpar2: f64,
    gpar1: f64,
    Sondenlaenge: f64,
    TMonitor: f64,
    u_min: f64,
}

#[test]
fn test_calc_substep() {
    let mut cfg_rs = PasConfig::new();
    let mut cfg_pas = PasConfig::new();
    let T_source = calculateEWS_rs(&mut cfg_rs);
    let T_source_ref = calculateEWS_pas(&mut cfg_pas);
    assert_almost_eq!(T_source, T_source_ref);
    assert_almost_eq_matr!(&cfg_rs.TEarth, &cfg_pas.TEarth);
    assert_almost_eq_arr!(cfg_rs.Q0, cfg_pas.Q0);
}

#[test]
fn test_calc_substep_0() {
    let mut cfg_rs = PasConfig::new();
    let mut cfg_pas = PasConfig::new();
    cfg_rs.Iteration = 0;
    cfg_pas.Iteration = 0;
    cfg_rs.simstep -= 1;
    cfg_pas.simstep -= 1;
    let T_source = calculateEWS_rs(&mut cfg_rs);
    let T_source_ref = calculateEWS_pas(&mut cfg_pas);
    assert_almost_eq!(T_source, T_source_ref);
    assert_almost_eq_matr!(&cfg_rs.TEarth, &cfg_pas.TEarth);
    assert_almost_eq_arr!(cfg_rs.Q0, cfg_pas.Q0);
}

impl PasConfig {
    fn new() -> Self {
        let u_min = -4.0;
        let Woche = DIM_T - 1;

        let mcpSole = 144014.53; // kJ/K
        let subdt = 97;
        let L1run = 905.79;
        let L1stop = 1507.91;
        let mut x = Def_cpSole * Def_Massenstrom as f64 / Def_AnzahlSonden as f64;
        if x < L1run {
            x = L1run;
        }
        let Lm_min = mcpSole / x;
        let dt = Def_Zeitschritt * 60;
        let dt_step = dt / subdt;
        let substep_run = ((Def_Sicherheit1 * dt_step) as f64 / Lm_min) as usize + 1;
        let substep_stop = ((Def_Sicherheit1 * dt_step) as f64 / mcpSole * L1stop) as usize + 1;

        let TEarth: Matrix = [
            [NAN; DIM_RAD + 3],
            [10.3, 10.3, 10.3, 10.3, 10.3, 10.3, 10.3, NAN],
            [11.3, 11.3, 11.3, 11.3, 11.3, 11.3, 11.3, NAN],
            [12.3, 12.3, 12.3, 12.3, 12.3, 12.3, 12.3, NAN],
            [NAN; DIM_RAD + 3],
        ];
        let mut T0 = [NAN; DIM_AXI + 1];
        for i in 1..=DIM_AXI {
            T0[i] = TEarth[i][DIM_RAD];
        }
        let mut TEarthOld = Matrix::new();
        for i in 1..=DIM_AXI {
            for j in 1..=DIM_RAD + 1 {
                TEarthOld[i][j] = TEarth[i][j];
            }
        }

        PasConfig {
            gpar1: NAN,
            gpar2: NAN,
            gpar3: NAN,
            gpar4: NAN,
            gpar5: NAN,
            gpar6: NAN,
            T0,
            TEarthOld,
            Iteration: 1,
            DimAxi: DIM_AXI,
            DimRad_: DIM_RAD,
            MonitorAxi: 0,
            MonitorRad: 0,
            TEarth,
            TUp: [0.; DIM_AXI + 1],
            TUpOld: [0.; DIM_AXI + 1],
            TDownOld: [0.; DIM_AXI + 1],
            TDown: [0.; DIM_AXI + 1],
            Q0Old: [0.; DIM_AXI + 1],
            Q0: [0.; DIM_AXI + 1],
            TSourceOld: 0.,
            TSource: 0.,
            TSourceMin: 0.,
            TSourceMax: 0.,
            TSink: 9.,
            TSinkMin: 0.,
            TSinkMax: 0.,
            QSource: Def_QSource,
            Massenstrom: Def_Massenstrom,
            cpSole: Def_cpSole,
            p: NAN,
            laminar: false,
            readFile: false,
            simstep: 1 + (Woche - 1) * 10080 / Def_Zeitschritt * Def_RepRandbed,
            StepWrite: 1,
            einschwingen: false,
            Allsteps: false,
            writeFile: false,
            Leistung: false,
            gfunction: true,
            RepRandbed: Def_RepRandbed,
            Zeitschritt: Def_Zeitschritt,
            Jahr: 1,
            numrows: Def_Simulationsdauer * 60 % Def_Zeitschritt,
            Starttemp: false,
            DeltaT: Def_DeltaT,
            subdt,
            AnzahlSonden: Def_AnzahlSonden,
            Rechenradius: Def_Rechenradius,
            Stationaer: false,
            mcpSole,
            substep_run,
            L1run: [0., 905.79, 905.79, 905.79],
            substep_stop,
            L1stop: [0., 1507.91, 1507.91, 1507.91],
            lambdaErde: [
                NAN,
                Def_lambdaErde,
                Def_lambdaErde + 0.1,
                Def_lambdaErde - 0.1,
                NAN,
                NAN,
                NAN,
                NAN,
                NAN,
                NAN,
            ],
            rhoErde: [NAN, 2600., 2500., 2600., NAN, NAN, NAN, NAN, NAN, NAN],
            cpErde: [NAN, 1000., 1010., 990., NAN, NAN, NAN, NAN, NAN, NAN],
            Q: [
                [0.; 53 * MAX_JAHRE],
                [NAN; 53 * MAX_JAHRE],
                [NAN; 53 * MAX_JAHRE],
                [NAN; 53 * MAX_JAHRE],
            ],
            B1: [
                [
                    [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0; DIM_RAD + 2],
                    [0.0; DIM_RAD + 2],
                    [0.0; DIM_RAD + 2],
                    [0.0; DIM_RAD + 2],
                    [0.0; DIM_RAD + 2],
                    [NAN; DIM_RAD + 2],
                ],
                [
                    [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [
                        3.33224144e-02,
                        9.58687328e-01,
                        7.97682872e-03,
                        1.34237716e-05,
                        5.26854727e-09,
                        5.04601074e-13,
                        3.49782250e-17,
                    ],
                    [
                        2.42895507e-05,
                        1.42773673e-03,
                        9.95189061e-01,
                        3.35759525e-03,
                        1.31778533e-06,
                        1.26212381e-10,
                        8.74886177e-15,
                    ],
                    [
                        8.64494708e-09,
                        5.08148902e-07,
                        7.10112100e-04,
                        9.98504925e-01,
                        7.84371038e-04,
                        7.51240234e-08,
                        5.20748989e-12,
                    ],
                    [
                        7.90680723e-13,
                        4.64761134e-11,
                        6.49479914e-08,
                        1.82786465e-04,
                        9.99625619e-01,
                        1.91516405e-04,
                        1.32756434e-08,
                    ],
                    [
                        1.81618290e-17,
                        1.06755002e-15,
                        1.49184655e-12,
                        4.19858032e-09,
                        4.59311293e-05,
                        9.99815440e-01,
                        1.38624347e-04,
                    ],
                    [NAN; DIM_RAD + 2],
                ],
                [
                    [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [
                        3.33200695e-02,
                        9.58549492e-01,
                        8.11566439e-03,
                        1.47674772e-05,
                        6.25334385e-09,
                        6.46170487e-13,
                        4.84846977e-17,
                    ],
                    [
                        2.54499880e-05,
                        1.49594709e-03,
                        9.94847189e-01,
                        3.62987661e-03,
                        1.53708493e-06,
                        1.58830050e-10,
                        1.19176396e-14,
                    ],
                    [
                        9.77239210e-09,
                        5.74419978e-07,
                        7.65989709e-04,
                        9.98387114e-01,
                        8.46224553e-04,
                        8.74420702e-08,
                        6.56112036e-12,
                    ],
                    [
                        9.64304301e-13,
                        5.66816855e-11,
                        7.55850936e-08,
                        1.97193611e-04,
                        9.99596093e-01,
                        2.06622251e-04,
                        1.55036752e-08,
                    ],
                    [
                        2.39760264e-17,
                        1.40930782e-15,
                        1.87931361e-12,
                        4.90293285e-09,
                        4.97170537e-05,
                        9.99800225e-01,
                        1.50052829e-04,
                    ],
                    [NAN; DIM_RAD + 2],
                ],
                [
                    [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [
                        3.33249178e-02,
                        9.58834477e-01,
                        7.82797122e-03,
                        1.26294002e-05,
                        4.74533384e-09,
                        4.35656603e-13,
                        2.89996267e-17,
                    ],
                    [
                        2.40541595e-05,
                        1.41390047e-03,
                        9.95341615e-01,
                        3.21922081e-03,
                        1.20958060e-06,
                        1.11048409e-10,
                        7.39197430e-15,
                    ],
                    [
                        8.19617559e-09,
                        4.81770170e-07,
                        6.79889491e-04,
                        9.98568615e-01,
                        7.50936317e-04,
                        6.89414857e-08,
                        4.58911293e-12,
                    ],
                    [
                        7.18574968e-13,
                        4.22377462e-11,
                        5.96072600e-08,
                        1.75218474e-04,
                        9.99641128e-01,
                        1.83581786e-04,
                        1.22201827e-08,
                    ],
                    [
                        1.58500493e-17,
                        9.31663905e-16,
                        1.31479394e-12,
                        3.86490147e-09,
                        4.41073123e-05,
                        9.99822770e-01,
                        1.33118868e-04,
                    ],
                    [NAN; DIM_RAD + 2],
                ],
            ],
            B2: [
                [
                    [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0; DIM_RAD + 2],
                    [0.0; DIM_RAD + 2],
                    [0.0; DIM_RAD + 2],
                    [0.0; DIM_RAD + 2],
                    [0.0; DIM_RAD + 2],
                    [NAN; DIM_RAD + 2],
                ],
                [
                    [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [
                        5.48656829e-02,
                        9.37231586e-01,
                        7.88944939e-03,
                        1.32767257e-05,
                        5.21083485e-09,
                        4.99073601e-13,
                        3.45950685e-17,
                    ],
                    [
                        3.99929840e-05,
                        1.41209710e-03,
                        9.95188997e-01,
                        3.35759515e-03,
                        1.31778529e-06,
                        1.26212377e-10,
                        8.74886150e-15,
                    ],
                    [
                        1.42339903e-08,
                        5.02582566e-07,
                        7.10112077e-04,
                        9.98504925e-01,
                        7.84371038e-04,
                        7.51240234e-08,
                        5.20748989e-12,
                    ],
                    [
                        1.30186358e-12,
                        4.59670074e-11,
                        6.49479893e-08,
                        1.82786465e-04,
                        9.99625619e-01,
                        1.91516405e-04,
                        1.32756434e-08,
                    ],
                    [
                        2.99036300e-17,
                        1.05585593e-15,
                        1.49184651e-12,
                        4.19858032e-09,
                        4.59311293e-05,
                        9.99815440e-01,
                        1.38624347e-04,
                    ],
                    [NAN; DIM_RAD + 2],
                ],
                [
                    [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [
                        5.48618642e-02,
                        9.37096753e-01,
                        8.02677042e-03,
                        1.46057234e-05,
                        6.18484859e-09,
                        6.39092735e-13,
                        4.79536264e-17,
                    ],
                    [
                        4.19036877e-05,
                        1.47956141e-03,
                        9.94847121e-01,
                        3.62987648e-03,
                        1.53708487e-06,
                        1.58830044e-10,
                        1.19176392e-14,
                    ],
                    [
                        1.60903520e-08,
                        5.68128137e-07,
                        7.65989683e-04,
                        9.98387114e-01,
                        8.46224553e-04,
                        8.74420702e-08,
                        6.56112036e-12,
                    ],
                    [
                        1.58773773e-12,
                        5.60608294e-11,
                        7.55850910e-08,
                        1.97193611e-04,
                        9.99596093e-01,
                        2.06622251e-04,
                        1.55036752e-08,
                    ],
                    [
                        3.94767936e-17,
                        1.39387113e-15,
                        1.87931355e-12,
                        4.90293285e-09,
                        4.97170537e-05,
                        9.99800225e-01,
                        1.50052829e-04,
                    ],
                    [NAN; DIM_RAD + 2],
                ],
                [
                    [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [
                        5.48697596e-02,
                        9.37375529e-01,
                        7.74221612e-03,
                        1.24910457e-05,
                        4.69334891e-09,
                        4.30884004e-13,
                        2.86819371e-17,
                    ],
                    [
                        3.96053774e-05,
                        1.39841125e-03,
                        9.95341553e-01,
                        3.21922071e-03,
                        1.20958056e-06,
                        1.11048406e-10,
                        7.39197407e-15,
                    ],
                    [
                        1.34950726e-08,
                        4.76492398e-07,
                        6.79889470e-04,
                        9.98568615e-01,
                        7.50936317e-04,
                        6.89414857e-08,
                        4.58911293e-12,
                    ],
                    [
                        1.18313977e-12,
                        4.17750335e-11,
                        5.96072581e-08,
                        1.75218474e-04,
                        9.99641128e-01,
                        1.83581786e-04,
                        1.22201827e-08,
                    ],
                    [
                        2.60972405e-17,
                        9.21457567e-16,
                        1.31479389e-12,
                        3.86490147e-09,
                        4.41073123e-05,
                        9.99822770e-01,
                        1.33118868e-04,
                    ],
                    [NAN; DIM_RAD + 2],
                ],
            ],
            Tneu: [[0.; DIM_RAD + 3]; DIM_AXI + 2],
            Sondenlaenge: Def_Sondenlaenge,
            TMonitor: NAN,
            u_min,
        }
    }
}

enum GenericTBrineMethod {
    Dynamic(libdhe::TBrineDynamicParameters),
    Stationary(libdhe::TBrineStationaryParameters),
}
impl libdhe::TBrineMethod for GenericTBrineMethod {
    fn refresh(
        &self,
        T_soil: &[f64],
        T_U: &mut [f64],
        Q_wall: &mut [f64],
        dim_ax: usize,
        T_sink: f64,
    ) -> f64 {
        match self {
            Self::Dynamic(obj) => obj.refresh(T_soil, T_U, Q_wall, dim_ax, T_sink),
            Self::Stationary(obj) => obj.refresh(T_soil, T_U, Q_wall, dim_ax, T_sink),
        }
    }
}

fn calculateEWS_rs(cfg: &mut PasConfig) -> f64 {
    let dim_ax = cfg.DimAxi;
    let dim_rad = cfg.DimRad_;
    let U_brine = cfg.cpSole * cfg.Massenstrom / cfg.AnzahlSonden as f64;
    let dt = cfg.Zeitschritt * 60;
    let dt_step = dt as f64 / cfg.subdt as f64;
    let L1: &[f64] = if U_brine > 0. {
        &cfg.L1run
    } else {
        &cfg.L1stop
    };
    let T_soil_tensor =
        flatten_tensor!(DIM_AXI, DIM_RAD)(if U_brine > 0. { &cfg.B1 } else { &cfg.B2 }).to_vec();
    let L = (&L1[1..]).to_vec();
    let pump_parameters: libdhe::TSoilParameters<GenericTBrineMethod> = if cfg.Stationaer {
        libdhe::TSoilParameters {
            T_soil_tensor,
            L,
            T_brine_method: GenericTBrineMethod::Stationary(T_brine_stationary_parameters_new(
                L1, dim_ax, U_brine,
            )),
        }
    } else {
        libdhe::TSoilParameters {
            T_soil_tensor,
            L,
            T_brine_method: GenericTBrineMethod::Dynamic(T_brine_dynamic_parameters_new(
                L1,
                dim_ax,
                if U_brine > 0. {
                    cfg.substep_run
                } else {
                    cfg.substep_stop
                },
                U_brine,
                cfg.mcpSole,
                dt_step as f64,
            )),
        }
    };
    let mut simstepn =
        (cfg.simstep + cfg.numrows * (cfg.Jahr - 1)) % (10080 / cfg.Zeitschritt * cfg.RepRandbed);
    if simstepn == 0 {
        simstepn = 10080 / cfg.RepRandbed / cfg.Zeitschritt;
    }
    let mut n_Q0 = (simstepn - 1) * cfg.subdt;
    let mut T_soil = vec![NAN; (DIM_RAD + 2) * dim_ax];
    let mut l = 0;
    for j in 0..dim_rad + 2 {
        for i in 1..=dim_ax {
            T_soil[l] = cfg.TEarth[i][j];
            l += 1;
        }
    }
    let mut sum_Q0 = vec![NAN; dim_ax];
    for i in 0..dim_ax {
        sum_Q0[i] = cfg.Q0[i + 1] * n_Q0 as f64;
    }
    let mut Q_wall = vec![0.; dim_ax];
    let mut T_U = T_U_from_pas(&cfg.TDown, &cfg.TUp);
    let n_steps = cfg.subdt;
    let mut T_source: f64;
    if cfg.Iteration == 0
        && ((cfg.simstep + cfg.numrows * (cfg.Jahr - 1)) * cfg.Zeitschritt)
            % (60 * 24 * 7 * cfg.RepRandbed)
            == 0
    {
        let mut T_soil_tensor = vec![NAN; dim_rad * (dim_rad + 2) * dim_ax];
        for i in 0..dim_rad * (dim_rad + 2) * dim_ax {
            T_soil_tensor[i] = pump_parameters.T_soil_tensor[i];
        }
        T_source = (n_steps - 1) as f64
            * libdhe::soil_step(
                &mut T_soil,
                cfg.TSink,
                &mut sum_Q0,
                dim_ax,
                dim_rad,
                n_steps - 1,
                &mut Q_wall,
                &mut T_U,
                &pump_parameters,
            );
        n_Q0 += n_steps - 1;
        let T_soil_tensor = id_tensor!(DIM_AXI, DIM_RAD)();
        T_source += libdhe::soil_step(
            &mut T_soil,
            cfg.TSink,
            &mut sum_Q0,
            dim_ax,
            dim_rad,
            1,
            &mut Q_wall,
            &mut T_U,
            &pump_parameters,
        );
        n_Q0 += 1;
        T_source /= n_steps as f64;
        let Woche: usize = if !cfg.Starttemp {
            (cfg.simstep + cfg.numrows * (cfg.Jahr - 1) - 1)
                / (10080 / cfg.Zeitschritt * cfg.RepRandbed)
                + 1
        } else {
            (cfg.simstep - 1) / (10080 / cfg.Zeitschritt * cfg.RepRandbed) + 1
        };
        let dim_t = Woche + 1;
        let mut T_soil_boundary = vec![NAN; dim_ax];
        let mut d_lambda_soil = vec![NAN; dim_ax];
        let t = t_range(dim_t, cfg.RepRandbed as f64 * 604800., 1);
        let mut c_V_soil = vec![NAN; dim_ax];
        for i in 0..dim_ax {
            c_V_soil[i] = cfg.cpErde[i + 1] * cfg.rhoErde[i + 1];
        }
        let g = if cfg.gfunction {
            let prm = libdhe::GFuncParametersCore {
                g_coefs: [
                    cfg.gpar1, cfg.gpar2, cfg.gpar3, cfg.gpar4, cfg.gpar5, cfg.gpar6,
                ],
                u_min: cfg.u_min,
                L: cfg.Sondenlaenge,
                go_const: libdhe::DEFAULT_GO_CONST,
            };
            prm.g_func(&t, &c_V_soil, &cfg.lambdaErde[1..], &[cfg.Rechenradius])
        } else {
            libdhe::GConeParameters {}.g_func(
                &t,
                &c_V_soil,
                &cfg.lambdaErde[1..],
                &[cfg.Rechenradius],
            )
        };
        let mut q = vec![NAN; dim_t * dim_ax];

        for j in 0..dim_ax {
            d_lambda_soil[j] = cfg.lambdaErde[j + 1] * cfg.Sondenlaenge / dim_ax as f64;
            cfg.Q[j + 1][Woche] = sum_Q0[j] / n_Q0 as f64;
            T_soil_boundary[j] = cfg.T0[j + 1];
        }
        l = 0;
        for i in 0..dim_t {
            for j in 0..dim_ax {
                q[l] = cfg.Q[j + 1][i];
                l += 1;
            }
        }

        let T_soil_boundary = Delta_T_boundary_1(&g, Woche, dim_ax, q, &d_lambda_soil);
        for j in 0..dim_ax {
            T_soil[(dim_rad + 1) * dim_ax + j] = T_soil_boundary[j];
        }
        libdhe::T_soil_refresh(&mut T_soil, &T_soil_tensor, dim_ax, dim_rad);
    } else {
        T_source = libdhe::soil_step(
            &mut T_soil,
            cfg.TSink,
            &mut sum_Q0,
            dim_ax,
            dim_rad,
            n_steps,
            &mut Q_wall,
            &mut T_U,
            &pump_parameters,
        );
        n_Q0 += n_steps;
    }
    l = 0;
    for j in 0..dim_rad + 2 {
        for i in 1..=dim_ax {
            cfg.TEarth[i][j] = T_soil[l];
            l += 1;
        }
    }
    for i in 0..dim_ax {
        cfg.Q0[i + 1] = sum_Q0[i] / n_Q0 as f64;
    }
    T_source
}

fn t_range(dim_t: usize, dt: f64, i0: usize) -> Vec<f64> {
    (i0..dim_t + i0).map(|i| dt * i as f64).collect()
}

fn calculateEWS_pas(cfg: &mut PasConfig) -> f64 {
    calculateEWSGeneric(
        cfg.Iteration,
        cfg.DimAxi,
        cfg.DimRad_,
        cfg.MonitorAxi,
        cfg.MonitorRad,
        &mut cfg.TEarthOld,
        &mut cfg.TEarth,
        &mut cfg.TUp,
        &mut cfg.TUpOld,
        &mut cfg.TDownOld,
        &mut cfg.TDown,
        &mut cfg.Q0Old,
        &mut cfg.Q0,
        cfg.TSourceOld,
        cfg.TSource,
        cfg.TSourceMin,
        cfg.TSourceMax,
        cfg.TSink,
        cfg.TSinkMin,
        cfg.TSinkMax,
        cfg.QSource,
        cfg.Massenstrom,
        cfg.cpSole,
        cfg.p,
        cfg.laminar,
        cfg.readFile,
        cfg.simstep,
        cfg.StepWrite,
        cfg.einschwingen,
        cfg.Allsteps,
        cfg.writeFile,
        cfg.Leistung,
        cfg.gfunction,
        cfg.RepRandbed,
        cfg.Zeitschritt,
        cfg.Jahr,
        cfg.numrows,
        cfg.Starttemp,
        cfg.DeltaT,
        cfg.subdt,
        cfg.AnzahlSonden,
        cfg.Rechenradius,
        cfg.Stationaer,
        cfg.mcpSole,
        cfg.substep_run,
        cfg.L1run,
        cfg.substep_stop,
        cfg.L1stop,
        cfg.lambdaErde,
        cfg.rhoErde,
        cfg.cpErde,
        &mut cfg.Q,
        cfg.T0,
        cfg.B1,
        cfg.B2,
        &mut cfg.Tneu,
        cfg.gpar6,
        cfg.gpar5,
        cfg.gpar4,
        cfg.gpar3,
        cfg.gpar2,
        cfg.gpar1,
        cfg.Sondenlaenge,
        cfg.TMonitor,
        cfg.u_min,
        TBRINE,
        RandAussen,
        RandAussen_gfunc,
    )
}

fn T_U_from_pas(TDown: &[f64], TUp: &[f64]) -> Vec<f64> {
    let dim_ax = TDown.len() - 1;
    let mut T_U = vec![NAN; 2 * dim_ax];
    for i in 0..dim_ax {
        T_U[i] = TDown[1 + i];
        T_U[dim_ax + i] = TUp[1 + i];
    }
    T_U
}

fn T_brine_stationary_parameters_new(
    L_pas: &[f64],
    dim_ax: usize,
    L0: f64,
) -> libdhe::TBrineStationaryParameters {
    libdhe::TBrineStationaryParameters {
        kappa_brine: (0..dim_ax)
            .map(|i| L0 / (0.5 * L_pas[i + 1] + L0))
            .collect(),
        kappa_soil: (0..dim_ax)
            .map(|i| L_pas[i + 1] / (L_pas[i + 1] + 2. * L0))
            .collect(),
        L: L_pas[1..=dim_ax].to_vec(),
    }
}
fn T_brine_dynamic_parameters_new(
    L_pas: &[f64],
    dim_ax: usize,
    substep: usize,
    L0: f64,
    mcpSole: f64,
    dt: f64,
) -> libdhe::TBrineDynamicParameters {
    libdhe::TBrineDynamicParameters {
        n_sub_steps: substep as u32,
        kappa_ax: L0 / mcpSole * dt / substep as f64,
        kappa_rad: (0..dim_ax)
            .map(|i| 0.5 * L_pas[i + 1] / substep as f64 * dt / mcpSole)
            .collect(),
        lambda_brine: (0..dim_ax)
            .map(|i| 0.5 * L_pas[i + 1] / substep as f64)
            .collect(),
    }
}

fn TBRINE(
    T: Matrix,
    TDown: &mut [f64],
    TUp: &mut [f64],
    TSink: f64,
    L0: f64,
    L: &[f64],
    _La: &[f64],
    Zeitschritt: usize,
    subdt: usize,
    substep: usize,
    QWand: &mut [f64],
    mcpSole: f64,
    _mcpSoleUp: f64,
    _mcpSoleDown: f64,
    DimAxi: usize,
    stationaer: bool,
    _KoaxialSonde: bool,
) -> f64 {
    let mut T_soil = vec![NAN; DimAxi];
    let mut T_U = T_U_from_pas(TDown, TUp);
    let T_out: f64;
    let dt = (Zeitschritt * 60) as f64 / subdt as f64;

    for i in 0..DimAxi {
        T_soil[i] = T[i + 1][1];
    }
    if stationaer {
        let prm = T_brine_stationary_parameters_new(L, DimAxi, L0);
        T_out = prm.refresh(&T_soil, &mut T_U, &mut QWand[1..], DimAxi, TSink);
    } else {
        let prm = T_brine_dynamic_parameters_new(L, DimAxi, substep, L0, mcpSole, dt);
        T_out = prm.refresh(&T_soil, &mut T_U, &mut QWand[1..], DimAxi, TSink);
    }
    for i in 1..=DimAxi {
        QWand[i] *= dt;
        TDown[i] = T_U[i - 1];
        TUp[i] = T_U[DIM_AXI + i - 1];
    }
    T_out
}

fn RandAussen_gfunc(
    k: usize,
    Woche: usize,
    _Zeitschritt: usize,
    _simstep: usize,
    RepRandbed: usize,
    Q: MatrixQ,
    cpErd: f64,
    rhoErd: f64,
    mut lambdaErd: f64,
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
    // Replacement for original code for tests
    let dim_t = Woche + 1;
    let t = t_range(dim_t, RepRandbed as f64 * 604800., 1);
    let c_V_soil = cpErd * rhoErd;
    let mut q = vec![NAN; dim_t];
    for i in 0..dim_t {
        q[i] = Q[k][i];
    }
    let prm = libdhe::GFuncParametersCore {
        g_coefs: [gpar1, gpar2, gpar3, gpar4, gpar5, gpar6],
        u_min,
        L: Sondenlaenge,
        go_const: libdhe::DEFAULT_GO_CONST,
    };
    let g = prm.g_func(&t, &[c_V_soil], &[lambdaErd], &[Rechenradius]);
    lambdaErd *= Sondenlaenge / DimAxi as f64;
    Delta_T_boundary_1(&g, dim_t - 1, 1, q, &[lambdaErd])[0]
}

fn RandAussen(
    k: usize,
    Woche: usize,
    _Zeitschritt: usize,
    _simstep: usize,
    RepRandbed: usize,
    Q: MatrixQ,
    cpErd: f64,
    rhoErd: f64,
    mut lambdaErd: f64,
    Rechenradius: f64,
    Sondenlaenge: f64,
    DimAxi: usize,
) -> f64 {
    let dim_t = Woche + 1;
    let t: Vec<f64> = (0..dim_t)
        .map(|i| (RepRandbed * 604800 * i) as f64)
        .collect();
    let c_V_soil = cpErd * rhoErd;
    let mut q = vec![NAN; dim_t];
    for i in 0..dim_t {
        q[i] = Q[k][i];
    }
    let g = libdhe::GConeParameters.g_func(&t, &[c_V_soil], &[lambdaErd], &[Rechenradius]);
    lambdaErd *= Sondenlaenge / DimAxi as f64;
    Delta_T_boundary_1(&g, dim_t - 1, 1, q, &[lambdaErd])[0]
}
