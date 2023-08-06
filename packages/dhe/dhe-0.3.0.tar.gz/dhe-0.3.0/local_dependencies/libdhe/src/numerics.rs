#![allow(clippy::many_single_char_names)]

pub fn arange(x0: f64, x1: f64, dx: f64) -> Vec<f64> {
    let n = ((x1 - x0) / dx) as usize;
    (0..n + 1).map(|i| x0 + i as f64 * dx).collect()
}

/*
/// Solves the Vandermonde linear system
/// \sum_{i=1}^N x_i^k w_i = q_k (k = 0, ... , N-1). Input consists of
/// the vectors x[0..n-1] and q[0..n-1] ; the vector w[0..n-1] is output.
pub fn solve_vandermonde_T(x: &[f64], q: &[f64], n: usize) -> Vec<f64> {
    if n == 1 { return q.to_vec(); }

    let mut b;
    let mut s;
    let mut t;
    let mut xx;
    let mut c = vec![0.; n];
    let mut w = vec![0.; n];

    c[n-1] = -x[0];
    // Coefficients of the master polynomial are found by recursion.
    for i in 1..n {
    xx = -x[i];
    for j in n-i-1..n-1 { c[j] += xx*c[j+1]; }
    c[n-1] += xx;
    }
    for i in 0..n { // Each subfactor in turn
    xx = x[i];
    t = 1.0; b = 1.0;
    s = q[n-1]; // <- A_{i n-1}
    for k in (1..n).rev() { // is synthetically divided,
        b = c[k] + xx*b;
        s += q[k-1]*b; // A_{i k-1}
        // matrix-multiplied by the right-hand side,
        t = xx*t + b;
    }
    w[i] = s/t; // and supplied with a denominator.
    }
    return w;
}
*/
/// Solves the Vandermonde linear system
/// \sum_{i=1}^N x_k^i w_i = q_k (k = 0, ... , N-1). Input consists of
/// the vectors x[0..n-1] and q[0..n-1] ; the vector w[0..n-1] is output.
pub fn solve_vandermonde(x: &[f64], q: &[f64], n: usize, w: &mut [f64]) {
    if n == 1 {
        w[0] = q[0];
        return;
    }

    let mut b;
    let mut a = vec![1.; n];
    let mut t;
    let mut xx;
    let mut c = vec![0.; n];

    c[n - 1] = -x[0];
    // Coefficients of the master polynomial are found by recursion.
    for i in 0..n {
        w[i] = 0.;
    }
    for i in 1..n {
        xx = -x[i];
        for j in n - i - 1..n - 1 {
            c[j] += xx * c[j + 1];
        }
        c[n - 1] += xx;
    }
    // w[k] = \sum_i A_{i k} q_i
    for i in 0..n {
        // Each subfactor in turn
        xx = x[i];
        t = 1.0;
        b = 1.0;
        for k in (1..n).rev() {
            // is synthetically divided,
            b = c[k] + xx * b;
            a[k - 1] = b; // A_{i k-1} = b / t_i
                          // matrix-multiplied by the right-hand side,
            t = xx * t + b;
        }
        for k in 0..n {
            w[k] += a[k] * q[i] / t;
        } // <- A_{i n-1} = 1/t_i
    }
}
/*
/// Solves a tridiagonal matrix equation
/// A x = b, where A is n x n and has diagonal `diag` and off-diagonals
/// `lower`, `upper`
/// b can have an additional dimension m. This will solve multiple
/// systems of equations and result in an output x of size m x n.
/// `diag` and `b` are overwritten, `b` ending up being the solution x.
pub fn solve_tridiagonal(diag: &mut [f64], upper: &[f64], lower: &[f64], b: &mut [f64], m: usize) {
    let mut w;
    let n = diag.len();
    for i in 1..n {
    w = diag[i] / lower[i-1];
    println!("[{}] {}, {}, {}", i, w, diag[i],  lower[i-1]);
    diag[i] -= w * upper[i-1];
    for j in 0..m {
        b[j*n + i] -= w * b[j*n + i-1];
    }
    }
    println!("b = {:?}", b);
    println!("diag = {:?}", diag);
    for j in 0..m {
    b[j*n + n-1] = b[j*n + n-1] / diag[n-1];
    for i in (0..n-1).rev() {
        b[j*n + i] = (b[j*n + i] - upper[i] * b[j*n + i+1]) / diag[i];
    }
    }
}
*/
/// Solves a tridiagonal matrix equation
/// A x = b, where A is n x n and has diagonal `diag` and off-diagonals
/// `lower`, `upper`
/// b can have an additional dimension m. This will solve multiple
/// systems of equations and result in an output x of size m x n.
/// `b` is overwritten, ending up being the solution x.
pub fn solve_tridiagonal(
    diag: &[f64],
    upper: &[f64],
    lower: &[f64],
    b: &mut [f64],
    m: usize,
) -> Result<(), String> {
    let n = diag.len();
    let mut bet = vec![0.; n];
    let mut gam = vec![0.; n]; // One vector of workspace, gam is needed.
    if diag[0] == 0.0 {
        return Err("Error 1 in tridiag".to_string());
    } //If this happens then you should rewrite your equations as a set of order N − 1, with u_1 trivially eliminated.
    bet[0] = diag[0];
    for i in 1..n {
        // Decomposition and forward substitution.
        gam[i] = upper[i - 1] / bet[i - 1];
        bet[i] = diag[i] - lower[i - 1] * gam[i];
        if bet[i] == 0.0 {
            return Err("Error 2 in tridiag".to_string());
        }
        // Algorithm fails; see below
    }
    for k in 0..m {
        let b_k = &mut b[k * n..(k + 1) * n];
        b_k[0] /= bet[0];
        for i in 1..n {
            b_k[i] = (b_k[i] - lower[i - 1] * b_k[i - 1]) / bet[i];
        }
        for i in (0..n - 1).rev() {
            b_k[i] -= gam[i + 1] * b_k[i + 1];
        }
        // Backsubstitution.
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    pub const EPS: f64 = 1.0E-10;
    macro_rules! assert_eq_delta {
        ($x:expr, $y:expr, $d: expr) => {
            if ($x - $y).abs() > $d {
                panic!(
                    "assertion failed: `(left == right)`\n  left: `{}`\n right: `{}`",
                    $x, $y
                );
            }
        };
    }
    /*
    macro_rules! assert_almost_eq {
    ($x:expr, $y:expr) => {
        assert_eq_delta!($x, $y, EPS);
    }
    }
     */
    macro_rules! assert_eq_arr_delta {
        ($x:expr, $y:expr, $d:expr) => {
            for i in 0..$x.len() {
                assert_eq_delta!($x[i], $y[i], $d)
            }
        };
    }

    macro_rules! assert_almost_eq_arr {
        ($x:expr, $y:expr) => {
            assert_eq_arr_delta!($x, $y, EPS);
        };
    }

    use super::solve_vandermonde;
    #[test]
    fn test_solve_vandermonde() {
        let x = [1., 2.];
        let mut w = [0.; 2];
        // P = x^2 -3 x + 2
        // P_1 = -x + 2, P_2 = x - 1 => A = [[2, -1], [-1, 1]]
        solve_vandermonde(&x, &[2., 3.], x.len(), &mut w);
        let ref_w = [1., 1.];
        assert_almost_eq_arr!(w, ref_w);

        let x = [1., 2., 3.];
        let mut w = [0.; 3];
        // P = x^3 -6 x^2 + 11 x - 6
        // P_1 = (x^2 - 5x + 6)/2    => a_1 = [3, -5/2, 1/2]
        // P_2 = (x^2 - 4x + 3)/(-1) => a_2 = [-3, 4, -1]
        // P_3 = (x^2 - 3x + 2)/2    => a_3 = [1, -3/2, 1/2]
        solve_vandermonde(&x, &[3., 7., 13.], x.len(), &mut w);
        let ref_w = [1., 1., 1.];
        assert_almost_eq_arr!(w, ref_w);

        let x = [1., 2., 3., 4., 5., 6.];
        let mut w = [0.; 6];
        solve_vandermonde(&x, &[6., 63., 364., 1365., 3906., 9331.], x.len(), &mut w);
        let ref_w = [1., 1., 1., 1., 1., 1.];
        assert_almost_eq_arr!(w, ref_w);
    }
    use super::solve_tridiagonal;
    #[test]
    fn test_solve_tridiagonal() {
        let diag = [1., 1., 1.];
        let upper = [0., 1.];
        let lower = [1., 0.];
        let mut b = [1., 3., 1.];
        solve_tridiagonal(&diag, &upper, &lower, &mut b, 1).unwrap();
        assert_almost_eq_arr!(b, [1., 1., 1.]);

        let diag = [1., 2., 1.];
        let upper = [1., 1.];
        let lower = [0., 0.];
        let mut b = [2., 3., 1., 1., 0., 0.];
        solve_tridiagonal(&diag, &upper, &lower, &mut b, 1).unwrap();
        assert_almost_eq_arr!(b, [1., 1., 1., 1., 0., 0.]);

        let diag = [
            4527058.640070025,
            38028438.734685145,
            193712619.79690066,
            861827803.8869578,
            3628452090.968371,
        ];
        let off_diag = [
            -763152.1625172902,
            -909894.9216469377,
            -1055050.6848450396,
            -1129841.2638285048,
        ];
        let mut b = [1373769.7405351724, 0.0, 0.0, 0.0, 0.0];
        solve_tridiagonal(&diag, &off_diag, &off_diag, &mut b, 1).unwrap();
        assert_almost_eq_arr!(
            b,
            [
                0.304487652605313,
                0.00611112464251796,
                2.8704987619414383e-05,
                3.514069640447911e-08,
                1.0942244197264381e-11
            ]
        );
    }
}
