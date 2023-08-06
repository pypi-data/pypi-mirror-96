#![allow(dead_code)]
pub const EPS: f64 = 1.0E-7;

#[macro_export]
macro_rules! assert_eq_arr_delta {
    ($x:expr, $y:expr, $d:expr) => {
        for i in 0..$x.len() {
            assert_eq_delta!($x[i], $y[i], $d)
        }
    };
}

#[macro_export]
macro_rules! assert_almost_eq_arr {
    ($x:expr, $y:expr) => {
        assert_eq_arr_delta!($x, $y, EPS);
    };
}

#[macro_export]
macro_rules! assert_almost_eq_matr {
    ($x:expr, $y:expr) => {
        for j in 0..$x.len() {
            assert_eq_arr_delta!($x[j], $y[j], EPS);
        }
    };
}

#[macro_export]
macro_rules! assert_eq_delta {
    ($x:expr, $y:expr, $d: expr) => {
        if (f64::is_nan($x) ^ f64::is_nan($y)) || ($x - $y).abs() > $d {
            panic!(
                "assertion failed: `(left == right)`\n  left: `{}`\n right: `{}`",
                $x, $y
            );
        }
    };
}

#[macro_export]
macro_rules! assert_almost_eq {
    ($x:expr, $y:expr) => {
        assert_eq_delta!($x, $y, EPS);
    };
}
