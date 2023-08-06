#![allow(non_snake_case)]

mod assert_arr;
mod shared;
use assert_arr::EPS;
mod original;
use original::{multiplizieren, KMatrix, Matrix, New, DIM_RAD_MAX};

use std::f64::NAN;

#[test]
fn test_tsoil() {
    const DIMAXI: usize = 2;
    const DIMRAD: usize = 3;

    let TEarth_data: Matrix = [
        [NAN; DIM_RAD_MAX + 2],
        [3.3, 10.3, 10.3, 10.3, 10.3, NAN, NAN, NAN],
        [4.3, 11.3, 11.3, 11.3, 11.3, NAN, NAN, NAN],
        [NAN; DIM_RAD_MAX + 2],
        [NAN; DIM_RAD_MAX + 2],
    ];
    let mut TEarth_new_data = Matrix::new();
    let B: KMatrix = [
        [
            [1.0, 0.0, 0.0, 0.0, 0.0, NAN, NAN],
            [0.0; DIM_RAD_MAX + 1],
            [0.0; DIM_RAD_MAX + 1],
            [0.0; DIM_RAD_MAX + 1],
            [NAN; DIM_RAD_MAX + 1],
            [NAN; DIM_RAD_MAX + 1],
            [NAN; DIM_RAD_MAX + 1],
        ],
        [
            [1.0, 0.0, 0.0, 0.0, 0.0, NAN, NAN],
            [3.33e-02, 9.58e-01, 7.97e-03, 1.34e-05, 5.26e-09, NAN, NAN],
            [2.42e-05, 1.42e-03, 9.95e-01, 3.35e-03, 1.31e-06, NAN, NAN],
            [8.64e-09, 5.08e-07, 7.10e-04, 9.98e-01, 7.84e-04, NAN, NAN],
            [NAN; DIM_RAD_MAX + 1],
            [NAN; DIM_RAD_MAX + 1],
            [NAN; DIM_RAD_MAX + 1],
        ],
        [
            [1.0, 0.0, 0.0, 0.0, 0.0, NAN, NAN],
            [3.33e-02, 9.58e-01, 8.11e-03, 1.47e-05, 6.25e-09, NAN, NAN],
            [2.54e-05, 1.49e-03, 9.94e-01, 3.62e-03, 1.53e-06, NAN, NAN],
            [9.77e-09, 5.74e-07, 7.65e-04, 9.98e-01, 8.46e-04, NAN, NAN],
            [NAN; DIM_RAD_MAX + 1],
            [NAN; DIM_RAD_MAX + 1],
            [NAN; DIM_RAD_MAX + 1],
        ],
        [[NAN; DIM_RAD_MAX + 1]; DIM_RAD_MAX + 1],
    ];

    let T_soil_tensor = flatten_tensor!(DIMAXI, DIMRAD)(&B);
    let mut T_soil = flatten_matrix!(DIMAXI, DIMRAD)(&TEarth_data);

    libdhe::T_soil_refresh(&mut T_soil, &T_soil_tensor, DIMAXI, DIMRAD);
    for i in 1..=DIMAXI {
        multiplizieren(&B, &TEarth_data, &mut TEarth_new_data, i, DIMRAD);
    }
    let T_soil_new = flatten_matrix!(DIMAXI, DIMRAD)(&TEarth_new_data);
    assert_almost_eq_arr!(T_soil_new, T_soil);
}

#[test]
fn test_tsoil_2() {
    const DIMAXI: usize = 1;
    const DIMRAD: usize = 5;
    let TEarth_data: Matrix = [
        [NAN; DIM_RAD_MAX + 2],
        [8.74435771, 11.3, 11.3, 11.3, 11.3, 11.3, 11.3, NAN],
        [NAN; DIM_RAD_MAX + 2],
        [NAN; DIM_RAD_MAX + 2],
        [NAN; DIM_RAD_MAX + 2],
    ];
    let mut TEarth_new_data = Matrix::new();
    let B: KMatrix = [
        [
            [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0; DIM_RAD_MAX + 1],
            [0.0; DIM_RAD_MAX + 1],
            [0.0; DIM_RAD_MAX + 1],
            [0.0; DIM_RAD_MAX + 1],
            [0.0; DIM_RAD_MAX + 1],
            [NAN; DIM_RAD_MAX + 1],
        ],
        [
            [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [
                4.04804839e-01,
                4.71896865e-01,
                1.20053553e-01,
                3.22436153e-03,
                2.03498764e-05,
                3.12523526e-08,
                3.50040651e-11,
            ],
            [
                5.90028078e-03,
                2.14538067e-02,
                9.20733367e-01,
                5.15864680e-02,
                3.25577091e-04,
                5.00005496e-07,
                5.60029037e-10,
            ],
            [
                3.34854688e-05,
                1.21755354e-04,
                1.09006096e-02,
                9.76451018e-01,
                1.24739529e-02,
                1.91568915e-05,
                2.14565952e-08,
            ],
            [
                4.90392187e-08,
                1.78309806e-07,
                1.59638612e-05,
                2.89449774e-03,
                9.94023556e-01,
                3.06232460e-03,
                3.42994370e-06,
            ],
            [
                1.81752786e-11,
                6.60865013e-11,
                5.91664453e-09,
                1.07278020e-06,
                7.39039784e-04,
                9.97023124e-01,
                2.23675729e-03,
            ],
            [NAN; DIM_RAD_MAX + 1],
        ],
        [[NAN; DIM_RAD_MAX + 1]; DIM_RAD_MAX + 1],
        [[NAN; DIM_RAD_MAX + 1]; DIM_RAD_MAX + 1],
    ];

    let T_soil_tensor = flatten_tensor!(DIMAXI, DIMRAD)(&B);
    let mut T_soil = flatten_matrix!(DIMAXI, DIMRAD)(&TEarth_data);

    libdhe::T_soil_refresh(&mut T_soil, &T_soil_tensor, DIMAXI, DIMRAD);
    for i in 1..=DIMAXI {
        multiplizieren(&B, &TEarth_data, &mut TEarth_new_data, i, DIMRAD);
    }
    let T_soil_new = flatten_matrix!(DIMAXI, DIMRAD)(&TEarth_new_data);

    assert_almost_eq_arr!(T_soil_new, T_soil);
}

#[test]
fn test_tsoil_id() {
    const DIMAXI: usize = 1;
    const DIMRAD: usize = 5;

    let mut T_soil: [f64; (DIMRAD + 2) * DIMAXI] = [0., 1., 2., 3., 4., 5., 6.];
    let T_soil_ref = T_soil;
    let T_soil_tensor = id_tensor!(DIMAXI, DIMRAD)();

    libdhe::T_soil_refresh(&mut T_soil, &T_soil_tensor, DIMAXI, DIMRAD);
    assert_almost_eq_arr!(T_soil, T_soil_ref);
}
