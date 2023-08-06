#![allow(non_snake_case)]

use libdhe::{TBrineDynamicParameters, TBrineMethod, TBrineStationaryParameters};

mod assert_arr;
mod original;
use assert_arr::EPS;
use original::{Matrix, Matrix_NAN, DIM_RAD_MAX, TBRINE};

const DIM_AXI: usize = 3;
const SIZE_AXI: usize = DIM_AXI + 1;

#[derive(Clone)]
struct Config {
    T: Matrix,
    TDown: [f64; SIZE_AXI],
    TUp: [f64; SIZE_AXI],
    TSink: f64,
    L0: f64,
    L: [f64; SIZE_AXI],
    La: [f64; SIZE_AXI],
    Zeitschritt: usize,
    subdt: usize,
    substep: usize,
    mcpSole: f64,
    mcpSoleUp: f64,
    mcpSoleDown: f64,
    stationaer: bool,
    Koaxialsonde: bool,
}

struct RustConfig {
    T_soil: [f64; DIM_AXI],
    T_U: [f64; 2 * DIM_AXI],
    dt: f64,
    T_sink: f64,
    stationary_parameters: TBrineStationaryParameters,
    dyn_parameters: TBrineDynamicParameters,
}

impl From<Config> for RustConfig {
    fn from(pas_c: Config) -> Self {
        let U_brine = pas_c.L0;
        let dt = pas_c.Zeitschritt as f64 * 60. / pas_c.subdt as f64;
        let kappa_ax = U_brine / pas_c.mcpSole * dt / pas_c.substep as f64;
        let mut kappa_brine = [0.; DIM_AXI];
        let mut kappa_soil = [0.; DIM_AXI];
        let mut kappa_rad = [0.; DIM_AXI];
        let mut lambda_brine = [0.; DIM_AXI];
        let mut T_soil = [0.; DIM_AXI];
        let mut L = [0.; DIM_AXI];
        let mut T_U = [0.; 2 * DIM_AXI];
        for i in 0..DIM_AXI {
            T_soil[i] = pas_c.T[1 + i][1];
            L[i] = pas_c.L[1 + i];
            T_U[i] = pas_c.TDown[1 + i];
            T_U[DIM_AXI + i] = pas_c.TUp[1 + i];
            kappa_brine[i] = U_brine / (0.5 * L[i] + U_brine);
            kappa_soil[i] = L[i] / (L[i] + 2. * U_brine);
            kappa_rad[i] = 0.5 * L[i] / pas_c.substep as f64 * dt / pas_c.mcpSole;
            lambda_brine[i] = 0.5 * L[i] / pas_c.substep as f64;
        }
        RustConfig {
            dt,
            T_sink: pas_c.TSink,
            dyn_parameters: TBrineDynamicParameters {
                n_sub_steps: pas_c.substep as u32,
                kappa_ax,
                kappa_rad: kappa_rad.to_vec(),
                lambda_brine: lambda_brine.to_vec(),
            },
            stationary_parameters: TBrineStationaryParameters {
                kappa_brine: kappa_brine.to_vec(),
                kappa_soil: kappa_soil.to_vec(),
                L: L.to_vec(),
            },
            T_soil,
            T_U,
        }
    }
}

use std::f64::NAN;
const fn T() -> Matrix {
    [
        [NAN; DIM_RAD_MAX + 2],
        [NAN, 2., NAN, NAN, NAN, NAN, NAN, NAN],
        [NAN, 3., NAN, NAN, NAN, NAN, NAN, NAN],
        [NAN, 4., NAN, NAN, NAN, NAN, NAN, NAN],
        [NAN; DIM_RAD_MAX + 2],
    ]
}
const CONFIGS: &[Config] = &[
    Config {
        T: T(),
        TDown: [0., 0., 0., 0.],
        TUp: [0., 0., 0., 0.],
        TSink: 30.,
        L0: 0.001,
        L: [NAN, 0.001, 0.03, 0.02],
        La: [0.001, 0.002, 0.003, 0.002],
        Zeitschritt: 3,
        subdt: 1,
        substep: 5,
        mcpSole: 0.37,
        mcpSoleUp: 0.65,
        mcpSoleDown: 0.8,
        stationaer: false,
        Koaxialsonde: false,
    },
    Config {
        T: T(),
        TDown: [NAN, 4.17812774, 2.33856008, 1.8860926],
        TUp: [NAN, 1.76708029, 1.6359369, 1.4983018],
        TSink: 30.,
        L0: 0.001,
        L: [NAN, 0.001, 0.03, 0.02],
        La: [0.001, 0.002, 0.003, 0.002],
        Zeitschritt: 3,
        subdt: 1,
        substep: 5,
        mcpSole: 0.37,
        mcpSoleUp: 0.65,
        mcpSoleDown: 0.8,
        stationaer: false,
        Koaxialsonde: false,
    },
    Config {
        T: T(),
        TDown: [0., 0., 0., 0.],
        TUp: [0., 0., 0., 0.],
        TSink: 0.,
        L0: 0.001,
        L: [NAN, 0.001, 0.03, 0.02],
        La: [0.001, 0.002, 0.003, 0.002],
        Zeitschritt: 1,
        subdt: 1,
        substep: 1,
        mcpSole: 0.37,
        mcpSoleUp: 0.65,
        mcpSoleDown: 0.8,
        stationaer: false,
        Koaxialsonde: false,
    },
    Config {
        T: Matrix_NAN,
        TDown: [NAN, 4.17812774, 2.33856008, 1.8860926],
        TUp: [NAN, 1.76708029, 1.6359369, 1.4983018],
        TSink: 0.,
        L0: 0.001,
        L: [NAN, 0.001, 0.03, 0.02],
        La: [0.001, 0.002, 0.003, 0.002],
        Zeitschritt: 1,
        subdt: 1,
        substep: 1,
        mcpSole: 0.37,
        mcpSoleUp: 0.65,
        mcpSoleDown: 0.8,
        stationaer: false,
        Koaxialsonde: false,
    },
];

#[test]
fn test_tbrine_U_stationary() {
    for cfg in CONFIGS.iter() {
        let mut cfg = cfg.clone();
        cfg.substep = 1;
        cfg.stationaer = true;
        let mut QWand: [f64; SIZE_AXI] = [0., 0., 0., 0.];
        let mut cfg_rust: RustConfig = cfg.clone().into();
        let T_out_ref = TBRINE(
            cfg.T,
            &mut cfg.TDown,
            &mut cfg.TUp,
            cfg.TSink,
            cfg.L0,
            &cfg.L,
            &cfg.La,
            cfg.Zeitschritt,
            cfg.subdt,
            cfg.substep,
            &mut QWand,
            cfg.mcpSole,
            cfg.mcpSoleUp,
            cfg.mcpSoleDown,
            DIM_AXI,
            cfg.stationaer,
            cfg.Koaxialsonde,
        );
        let mut Q_wall: [f64; DIM_AXI] = [0., 0., 0.];
        let T_out = cfg_rust.stationary_parameters.refresh(
            &cfg_rust.T_soil,
            &mut cfg_rust.T_U,
            &mut Q_wall,
            DIM_AXI,
            cfg_rust.T_sink,
        );
        assert_almost_eq!(T_out, T_out_ref);
        assert_almost_eq_arr!(&cfg.TDown[1..], cfg_rust.T_U);
        assert_almost_eq_arr!(&cfg.TUp[1..], &cfg_rust.T_U[DIM_AXI..]);
        for i in 0..DIM_AXI {
            assert_almost_eq!(QWand[1 + i], Q_wall[i] * cfg_rust.dt);
        }
    }
}
#[test]
fn test_tbrine_U_dynamic() {
    for cfg in CONFIGS.iter() {
        let mut cfg = cfg.clone();
        let mut QWand: [f64; SIZE_AXI] = [0., 0., 0., 0.];
        let mut cfg_rust: RustConfig = cfg.clone().into();
        let T_out_ref = TBRINE(
            cfg.T,
            &mut cfg.TDown,
            &mut cfg.TUp,
            cfg.TSink,
            cfg.L0,
            &cfg.L,
            &cfg.La,
            cfg.Zeitschritt,
            cfg.subdt,
            cfg.substep,
            &mut QWand,
            cfg.mcpSole,
            cfg.mcpSoleUp,
            cfg.mcpSoleDown,
            DIM_AXI,
            cfg.stationaer,
            cfg.Koaxialsonde,
        );
        let mut Q_wall: [f64; DIM_AXI] = [0., 0., 0.];
        let T_out = cfg_rust.dyn_parameters.refresh(
            &cfg_rust.T_soil,
            &mut cfg_rust.T_U,
            &mut Q_wall,
            DIM_AXI,
            cfg_rust.T_sink,
        );
        assert_almost_eq!(T_out, T_out_ref);
        assert_almost_eq_arr!(&cfg.TDown[1..], cfg_rust.T_U);
        assert_almost_eq_arr!(&cfg.TUp[1..], cfg_rust.T_U[DIM_AXI..]);
        for i in 0..DIM_AXI {
            assert_almost_eq!(QWand[1 + i], Q_wall[i] * cfg_rust.dt);
        }
    }
}
