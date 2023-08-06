#![allow(non_snake_case)]
#![allow(clippy::manual_memcpy)]

use std::f64::consts::PI;
use std::f64::NAN;
mod assert_arr;
mod shared;
use assert_arr::EPS;
mod original;
use original::{
    alpha1 as alpha1_pas, multiplizieren, r_grid as r_grid_pas, resistances,
    rz_grid as rz_grid_pas, Anfangstemp, C_matrix as C_matrix_pas, Def_Bodenerwaermung,
    Def_Bohrdurchmesser, Def_Gitterfaktor, Def_Jahresmitteltemp, Def_Rb, Def_Rechenradius,
    Def_Sicherheit2, Def_Sondenabstand, Def_Sondendurchmesser, Def_Sondenlaenge, Def_Zeitschritt,
    Def_adiabat, Def_cpErde, Def_cpFill, Def_g1, Def_g2, Def_g3, Def_g4, Def_g5,
    Def_g_Sondenabstand, Def_lambdaErde, Def_lambdaFill, Def_lambdaSole, Def_rhoErde, Def_rhoFill,
    KMatrix, L1run_matrix, Matrix, New, Optimaler_Zeitfaktor, Polynom, Vektor, VektorRad, _B,
};

#[test]
fn test_g_poly() {
    let g = [Def_g1, Def_g2, Def_g3, Def_g4, Def_g5];
    let (uMin, w) = Polynom(
        Def_g1,
        Def_g2,
        Def_g3,
        Def_g4,
        Def_g5,
        Def_Sondenabstand,
        Def_g_Sondenabstand,
    );
    let (u_min, g_coefs) =
        libdhe::g_poly(&g, Def_Sondenabstand, Def_g_Sondenabstand, 0.05).unwrap();
    assert_almost_eq_arr!(w, g_coefs);
    assert_almost_eq!(u_min, uMin);
}

#[test]
fn test_r() {
    const DIM_RAD: usize = 5;
    let Rechengebiet = Def_Rechenradius - Def_Bohrdurchmesser / 2.;
    let r_ref = r_grid_pas(
        Def_Sondendurchmesser,
        Def_Bohrdurchmesser,
        Rechengebiet,
        Def_Gitterfaktor,
        DIM_RAD,
    );
    let r = libdhe::r_grid(
        Def_Sondendurchmesser,
        Def_Bohrdurchmesser,
        Rechengebiet,
        DIM_RAD,
        Def_Gitterfaktor,
    );
    assert_almost_eq_arr!(r, r_ref[..r.len()]);
}

#[test]
fn test_rz() {
    const DIM_RAD: usize = 5;
    let r = [0.013, 0.0575, 0.461 / 3., 0.346, 2.192 / 3., 1.5];
    let mut r_ref = VektorRad::new();
    r_ref[..r.len()].copy_from_slice(&r);
    let rz_ref = rz_grid_pas(&r_ref, DIM_RAD);
    let rz = libdhe::rz_grid(&r);
    assert_almost_eq_arr!(rz, rz_ref[..DIM_RAD + 2]);
}

#[test]
fn test_alpha1() {
    let d_DHE = 0.;
    let D_DHE = 0.026;
    let Phi_m = 0.4;
    let brine_properties = libdhe::FluidProperties {
        c: 3875.,
        rho: 1050.,
        nu: 0.00000415,
        lambda: 0.449,
    };
    let alpha = libdhe::alpha1(
        &brine_properties,
        Phi_m / brine_properties.rho,
        D_DHE,
        d_DHE,
    );
    let alpha_ref = alpha1_pas(
        brine_properties.nu,
        brine_properties.rho,
        brine_properties.c,
        brine_properties.lambda,
        Phi_m,
        D_DHE,
        d_DHE,
    );
    assert_almost_eq!(alpha, alpha_ref);
}
#[test]
fn test_resistances() {
    let r = [0.013, 0.0575, 0.461 / 3., 0.346, 2.192 / 3., 1.5];
    let rz = libdhe::rz_grid(&r);
    let DimAxi = 3;
    let dl = Def_Sondenlaenge / DimAxi as f64;
    let alpha = 75.29384615384616;
    let lambdaErde = [
        NAN,
        Def_lambdaErde,
        Def_lambdaErde + 0.1,
        Def_lambdaErde - 0.1,
    ];
    for (Ra, Rb) in &[(0.01, Def_Rb), (0., Def_Rb), (0., 0.)] {
        let R1 = libdhe::R_1(dl, &r, &rz, alpha, Def_lambdaFill, *Ra, *Rb);
        let R2 = libdhe::R_2(dl, &r, &rz, Def_lambdaFill, &lambdaErde[1..], *Ra, *Rb);
        let (L1run, L1stop, R1_ref, R2_ref) = resistances(
            DimAxi,
            0.,
            dl,
            &r,
            &rz,
            alpha,
            &lambdaErde,
            Def_lambdaSole,
            Def_lambdaFill,
            *Ra,
            *Rb,
            Def_Sondendurchmesser,
        );
        assert_almost_eq!(R1, R1_ref);
        assert_almost_eq_arr!(&R2, &R2_ref[1..DimAxi + 1]);
        let L1_on = 1. / R1;
        let L1_off = 1.
            / (R1
                + (1. / libdhe::alpha0(Def_lambdaSole, Def_Sondendurchmesser) - 1. / alpha)
                    / (8. * PI * r[0] * dl));
        assert_almost_eq!(L1_on, L1run);
        assert_almost_eq!(L1_off, L1stop);
    }
}
#[test]
fn test_T_soil_0() {
    let TMittel = Def_Jahresmitteltemp + Def_Bodenerwaermung;
    let r = [0.013, 0.0575, 0.461 / 3., 0.346, 2.192 / 3., 1.5];
    let rz = libdhe::rz_grid(&r);
    const DIM_AXI: usize = 3;
    const DIM_RAD: usize = 5;
    let dl = Def_Sondenlaenge / DIM_AXI as f64;
    let T_grad = 0.03;
    let g = [Def_g1, Def_g2, Def_g3, Def_g4, Def_g5];
    let (u_min, g_coefs) =
        libdhe::g_poly(&g, Def_Sondenabstand, Def_g_Sondenabstand, 0.05).unwrap();
    let mut q_drain_pas = Vektor::new();
    let q_drain: &mut [f64] = &mut q_drain_pas[1..=DIM_AXI];
    q_drain[0] = 0.;
    q_drain[1] = 0.;
    q_drain[2] = 1.;

    let mut TEarth = Matrix::new();
    for y in &[0, 1] {
        let T_soil = libdhe::T_soil_0(
            *y as f64 * 3600. * 24. * 365.,
            g_coefs,
            DIM_AXI,
            dl,
            &[Def_rhoErde * Def_cpErde; DIM_AXI],
            &[Def_lambdaErde; DIM_AXI],
            &rz,
            TMittel,
            &q_drain_pas[1..=DIM_AXI],
            T_grad,
            u_min,
        );
        Anfangstemp(
            TMittel,
            T_grad,
            dl,
            q_drain_pas,
            &mut TEarth,
            &mut Vektor::new(),
            &mut Vektor::new(),
            &mut Vektor::new(),
            &mut Vektor::new(),
            &mut Vektor::new(),
            NAN,
            DIM_AXI,
            DIM_RAD,
            *y,
            g_coefs[0],
            g_coefs[1],
            g_coefs[2],
            g_coefs[3],
            g_coefs[4],
            g_coefs[5],
            Def_lambdaErde,
            Def_rhoErde,
            Def_cpErde,
            u_min,
            &rz,
            Def_Sondenlaenge,
        );
        assert_almost_eq_arr!(T_soil, flatten_matrix!(DIM_AXI, DIM_RAD)(&TEarth));
    }
}
#[test]
fn test_L_pump() {
    let r = [0.013, 0.0575, 0.461 / 3., 0.346, 2.192 / 3., 1.5];
    let rz = libdhe::rz_grid(&r);
    const DIM_AXI: usize = 3;
    const DIM_RAD: usize = 5;
    let dl = Def_Sondenlaenge / DIM_AXI as f64;

    let lambdaErde = [
        NAN,
        Def_lambdaErde,
        Def_lambdaErde + 0.1,
        Def_lambdaErde - 0.1,
    ];
    let R2_pas = [NAN, 0.00460078, 0.00452098, 0.00468898];
    let R2 = &R2_pas[1..];
    let L1_on = 40000. / 3.;
    let L1_off = -2733.456633111457;
    let (L_on, L_off) = libdhe::L_pump(
        dl,
        &r,
        &rz,
        L1_on,
        L1_off,
        R2,
        Def_adiabat,
        &lambdaErde[1..],
    );
    let (L_on_ref, L_off_ref) = L1run_matrix(
        DIM_AXI,
        DIM_RAD,
        L1_on,
        L1_off,
        &R2_pas,
        &lambdaErde,
        &r,
        &rz,
        dl,
        Def_adiabat,
    );
    assert_almost_eq_arr!(
        &L_on,
        flatten_matrix_raw![Matrix; 1,DIM_AXI + 1; 1,DIM_RAD + 2](&L_on_ref)
    );
    assert_almost_eq_arr!(
        &L_off,
        flatten_matrix_raw![Matrix; 1,DIM_AXI + 1; 1,DIM_RAD + 2](&L_off_ref)
    );
}

#[test]
fn test_C_matrix() {
    const DIM_AXI: usize = 3;
    const DIM_RAD: usize = 5;
    let dl = Def_Sondenlaenge / DIM_AXI as f64;
    let r = [0.013, 0.0575, 0.461 / 3., 0.346, 2.192 / 3., 1.5];
    let cpErde = [NAN, 1000., 1010., 990.];
    let rhoErde = [NAN, 2600., 2500., 2600.];
    let c_V_soil: Vec<f64> = rhoErde
        .iter()
        .zip(cpErde.iter())
        .map(|(x, y)| x * y)
        .collect();

    let C_ref = C_matrix_pas(
        DIM_AXI,
        DIM_RAD,
        &r,
        dl,
        &cpErde,
        &rhoErde,
        Def_cpFill,
        Def_rhoFill,
    );
    let C = libdhe::C_matrix(dl, &r, Def_cpFill * Def_rhoFill, &c_V_soil[1..]);
    assert_almost_eq_arr!(
        &C,
        flatten_matrix_raw![Matrix;1,DIM_AXI + 1; 1,DIM_RAD + 1](&C_ref)
    );
}

#[test]
fn test_optimal_n_steps() {
    let dt = Def_Zeitschritt * 60;
    const DIM_AXI: usize = 3;
    const DIM_RAD: usize = 5;
    let C = [
        [9.88e+05, 5.52e+06, 2.61e+07, 1.12e+08, 4.67e+08],
        [9.88e+05, 5.36e+06, 2.54e+07, 1.09e+08, 4.53e+08],
        [9.88e+05, 5.47e+06, 2.59e+07, 1.11e+08, 4.62e+08],
    ];
    let L = [
        [
            40000. / 3.,
            217.35444859,
            500.965279,
            552.124962,
            578.11550952,
            1744.47884119,
        ],
        [
            40000. / 3.,
            221.19098072,
            526.01354295,
            579.7312101,
            607.021285,
            1831.70278325,
        ],
        [
            40000. / 3.,
            213.26599815,
            475.91701505,
            524.5187139,
            549.20973405,
            1657.25489913,
        ],
    ];
    let mut C_pas = Matrix::new();
    let mut L_pas = Matrix::new();
    for i in 0..C.len() {
        for j in 0..C[0].len() {
            C_pas[i + 1][j + 1] = C[i][j];
            L_pas[i + 1][j + 1] = L[i][j];
        }
    }
    let optfak = Optimaler_Zeitfaktor(
        DIM_AXI,
        Def_Zeitschritt,
        L_pas,
        C_pas,
        false,
        Def_Sicherheit2 as f64,
    );
    let n_steps = libdhe::optimal_n_steps(
        &flatten_matrix_raw![0,DIM_AXI;0,DIM_RAD+1](&L),
        &flatten_matrix_raw![0,DIM_AXI;0,DIM_RAD](&C),
        DIM_AXI,
        DIM_RAD,
        dt as f64,
        Def_Sicherheit2 as f64,
    );
    assert_eq!(optfak, n_steps);
}

#[test]
fn test_B() {
    const DIM_AXI: usize = 3;
    const DIM_RAD: usize = 5;
    let dl = Def_Sondenlaenge / DIM_AXI as f64;
    let mut L_pas = Matrix::new();
    let L = [
        [40000. / 3., 217.35, 500.96, 552.12, 578.11, 1744.47],
        [40000. / 3., 221.19, 526.01, 579.73, 607.02, 1831.70],
        [40000. / 3., 213.26, 475.91, 524.51, 549.20, 1657.25],
    ];
    for i in 0..DIM_AXI {
        for j in 0..DIM_RAD + 1 {
            L_pas[i + 1][j + 1] = L[i][j];
        }
    }
    let r = [0.013, 0.0575, 0.461 / 3., 0.346, 2.192 / 3., 1.5];
    let mut r_ref = VektorRad::new();
    r_ref[..r.len()].copy_from_slice(&r);
    let cpErde = [NAN, 1000., 1010., 990.];
    let rhoErde = [NAN, 2600., 2500., 2600.];

    let C_pas = C_matrix_pas(DIM_AXI, DIM_RAD, &r, dl, &cpErde, &rhoErde, 3040., 1180.);
    let C = flatten_matrix_raw![Matrix;1,DIM_AXI+1;1,DIM_RAD+1](&C_pas);

    let dt_step = 3600.;
    let B = libdhe::T_soil_evolution(
        &flatten_matrix_raw![0,DIM_AXI;0,DIM_RAD+1](&L),
        &C,
        dt_step,
        DIM_AXI,
        DIM_RAD,
    );
    let B_pas = _B(&L_pas, &C_pas, dt_step, DIM_AXI, DIM_RAD);
    assert_almost_eq_arr!(&B, flatten_tensor!(DIM_AXI, DIM_RAD)(&B_pas));

    let mut T_old_pas = Matrix::new();
    let mut T_new_pas = Matrix::new();
    let mut T_old = [[NAN; DIM_AXI]; DIM_RAD + 2];
    for i in 0..DIM_AXI {
        for j in 0..DIM_RAD + 2 {
            T_old[j][i] = 10. + 0.1 * i as f64 - 0.2 * j as f64;
            T_old_pas[i + 1][j] = T_old[j][i];
        }
    }

    for i in 1..=DIM_AXI {
        multiplizieren(&B_pas, &T_old_pas, &mut T_new_pas, i, DIM_RAD);
    }
    let mut T_new = flatten_matrix_raw![0,DIM_RAD+2;0,DIM_AXI](&T_old);
    libdhe::T_soil_refresh(&mut T_new, &B, DIM_AXI, DIM_RAD);
    let mut T_new_T = [NAN; DIM_AXI * (DIM_RAD + 2)];
    for i in 0..DIM_AXI {
        for j in 0..DIM_RAD + 2 {
            T_new_T[i * (DIM_RAD + 2) + j] = T_new[j * DIM_AXI + i];
        }
    }
    assert_almost_eq_arr!(
        T_new_T,
        flatten_matrix_raw![Matrix; 1,DIM_AXI+1;0,DIM_RAD+2](&T_new_pas)
    );
    for i in 0..DIM_AXI {
        for j in 0..DIM_RAD + 2 {
            T_new_pas[i + 1][j] = NAN;
        }
    }
    for i in 0..T_new_pas.len() {
        for j in 0..T_new_pas[0].len() {
            if !T_new_pas[i][j].is_nan() {
                panic!("T_new_pas[{}][{}] = {} != NAN", T_new_pas[i][j], i, j);
            }
        }
    }
}
