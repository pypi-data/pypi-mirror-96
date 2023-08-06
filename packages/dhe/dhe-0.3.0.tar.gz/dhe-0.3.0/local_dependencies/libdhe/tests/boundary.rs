#![allow(non_snake_case)]

use std::f64::NAN;

use libdhe::{BoundaryMethod, GConeParameters, GFuncParametersCore, DEFAULT_GO_CONST};
mod assert_arr;
mod original;
mod shared;
use assert_arr::EPS;
use original::{MatrixQ, RandAussen, RandAussen_gfunc, DIM_AXI_MAX, MAX_JAHRE};
use shared::Delta_T_boundary_1;

const DIM_AXI: usize = 2;
const DIM_T: usize = 4;

const SIZE_AXI: usize = DIM_AXI + 1;

#[derive(Clone)]
struct Config {
    Woche: usize,
    RepRandBed: usize,
    c_p_soil: f64,
    r: f64,
    L: f64,
    rho_soil: [f64; DIM_AXI],
    c_V_soil: [f64; DIM_AXI],
    lambda_soil: [f64; SIZE_AXI],
    d_lambda_soil: [f64; SIZE_AXI],
    t: [f64; DIM_T],
    Q: [f64; (DIM_T + 1) * DIM_AXI],
    Q_pas: MatrixQ,
    Q1: [f64; DIM_T + 1],
    Trt_ref: [f64; DIM_AXI],
}

impl Config {
    fn new() -> Self {
        let c_p_soil = 1000.;
        let rho_soil: [f64; DIM_AXI] = [2600., 2650.];
        let lambda_soil: [f64; SIZE_AXI] = [2.5, 1.5, NAN];
        let L = 100.;
        let mut c_V_soil = [0.; DIM_AXI];
        let mut d_lambda_soil = [0.; SIZE_AXI];
        let mut t = [0.; DIM_T];
        let mut Q = [0.; (DIM_T + 1) * DIM_AXI];
        let mut Q_pas: MatrixQ = [[0.; 53 * MAX_JAHRE]; DIM_AXI_MAX];
        let mut Q1 = [0.; DIM_T + 1];
        let Trt_ref = [0.; DIM_AXI];
        let RepRandBed = 1;
        for i in 0..DIM_AXI {
            c_V_soil[i] = c_p_soil * rho_soil[i];
            d_lambda_soil[i] = lambda_soil[i] * L / DIM_AXI as f64;
        }
        for i in 0..DIM_T {
            t[i] = ((i + 1) * 604800 * RepRandBed) as f64;
        }
        for i in 0..(DIM_T + 1) * DIM_AXI {
            Q[i] = (i * i) as f64;
        }
        for i in 0..=DIM_T {
            Q1[i] = Q[i * DIM_AXI];
        }
        let mut l: usize = 0;
        for i in 0..=DIM_T {
            for j in 0..DIM_AXI {
                Q_pas[j + 1][i] = Q[l];
                l += 1;
            }
        }
        Config {
            Woche: 4,
            RepRandBed,
            c_p_soil,
            rho_soil,
            lambda_soil,
            d_lambda_soil,
            c_V_soil,
            r: 1.5,
            L,
            t,
            Q,
            Q_pas,
            Q1,
            Trt_ref,
        }
    }
}

#[test]
fn test_boundary() {
    let mut c = Config::new();
    for k in 0..DIM_AXI {
        c.Trt_ref[k] = RandAussen(
            k + 1,
            c.Woche,
            0,
            0,
            c.RepRandBed,
            c.Q_pas,
            c.c_p_soil,
            c.rho_soil[k],
            c.lambda_soil[k],
            c.r,
            c.L,
            DIM_AXI,
        );
    }
    let g = GConeParameters {}.g_func(&c.t, &[c.c_V_soil[0]], &c.lambda_soil, &[c.r]);
    let T_out = Delta_T_boundary_1(&g, DIM_T, 1, c.Q1.to_vec(), &c.d_lambda_soil);
    assert_eq_arr_delta!(&T_out, &[c.Trt_ref[0]], 1.0E-5);

    let g = GConeParameters {}.g_func(&c.t, &c.c_V_soil, &c.lambda_soil, &[c.r]);
    let T_out = Delta_T_boundary_1(&g, DIM_T, DIM_AXI, c.Q.to_vec(), &c.d_lambda_soil);
    assert_eq_arr_delta!(&T_out, c.Trt_ref, 1.0E-5);
}

#[test]
fn test_boundary_gfunc() {
    let mut c = Config::new();
    let prm = GFuncParametersCore {
        g_coefs: [0.1, 0.3, -0.2, 0.11, -0.001, 0.5],
        u_min: 0.5,
        go_const: DEFAULT_GO_CONST,
        L: c.L,
    };
    let c_g = &prm.g_coefs;
    for k in 0..DIM_AXI {
        c.Trt_ref[k] = RandAussen_gfunc(
            k + 1,
            c.Woche,
            0,
            0,
            c.RepRandBed,
            c.Q_pas,
            c.c_p_soil,
            c.rho_soil[k],
            c.lambda_soil[k],
            c.r,
            c.L,
            c_g[0],
            c_g[1],
            c_g[2],
            c_g[3],
            c_g[4],
            c_g[5],
            DIM_AXI,
            prm.u_min,
        );
    }
    let g = prm.g_func(&c.t, &[c.c_V_soil[0]], &c.lambda_soil, &[c.r]);
    let T_out = Delta_T_boundary_1(&g, DIM_T, 1, c.Q1.to_vec(), &c.d_lambda_soil);
    assert_almost_eq_arr!(&T_out, &[c.Trt_ref[0]]);

    let g = prm.g_func(&c.t, &c.c_V_soil, &c.lambda_soil, &[c.r]);
    let T_out = Delta_T_boundary_1(&g, DIM_T, DIM_AXI, c.Q.to_vec(), &c.d_lambda_soil);
    assert_almost_eq_arr!(&T_out, c.Trt_ref);
}

#[test]
fn test_gcone() {
    let t = [604800.0, 1209600.0, 1814400.0, 2419200.0];
    let c_V_soil = [2600000.0; 2];
    let lambda_soil = [2.4; 2];
    let r = [2.5];
    let g = GConeParameters {}.g_func(&t, &c_V_soil, &lambda_soil, &r);
    println!("g: {:?}", g);
    assert_almost_eq_arr!(
        &g,
        &[
            0.,
            0.,
            0.,
            0.,
            0.12298132961836304,
            0.12298132961836304,
            0.18687231578224872,
            0.18687231578224872
        ]
    );
}
