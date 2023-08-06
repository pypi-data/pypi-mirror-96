#![allow(non_snake_case)]
#![allow(dead_code)]

pub fn Delta_T_boundary_1(
    g: &[f64],
    dim_t: usize,
    dim_ax: usize,
    q: Vec<f64>,
    d_lambda_soil: &[f64],
) -> Vec<f64> {
    let prm = libdhe::TSoilParameters::<()> {
        T_soil_tensor: Vec::new(),
        L: Vec::new(),
        T_brine_method: (),
    };
    let dhe = libdhe::DHECore {
        g: g.to_vec(),
        d_lambda_soil: d_lambda_soil.to_vec(),
        L: 0.,
        R: 0.,
        x: 0.,
        y: 0.,
        L1_on: 0.,
        n_steps: 0,
        pump_dependent_parameters: [prm.clone(), prm],
    };
    let v_dhe = [dhe];
    let field = libdhe::DHEField::new(&v_dhe, dim_t, dim_ax);
    let dim_rad = 1;
    let mut states = [libdhe::DHEState {
        Q: q,
        T_soil: vec![0.; dim_ax * (dim_rad + 2)],
        T_U: Vec::new(),
        T_sink: 0.,
    }];
    field.Delta_T_boundary(&mut states, dim_t, dim_ax, dim_rad);
    states[0].T_soil[dim_ax * (dim_rad + 1)..].to_vec()
}

#[macro_export]
macro_rules! id_tensor {
    ($DIM_AX: expr, $DIM_RAD: expr) => {
        || -> [f64; $DIM_RAD * ($DIM_RAD + 2) * $DIM_AX] {
            let mut T_soil_tensor = [NAN; $DIM_RAD * ($DIM_RAD + 2) * $DIM_AX];
            let mut l = 0;
            for j in 0..$DIM_RAD {
                for k in 0..$DIM_RAD + 2 {
                    for _ in 0..$DIM_AX {
                        T_soil_tensor[l] = if j + 1 == k { 1. } else { 0. };
                        l += 1;
                    }
                }
            }
            T_soil_tensor
        }
    };
}

#[macro_export]
macro_rules! T{
    [$n:expr] => {
	|m: &[f64]| -> Vec<f64> {
	    let mut out = Vec::with_capacity(m.len());
	    let N = m.len() / $n;
	    if m.len() % $n != 0 { panic!("T!: {} x {} != {}", $n, N, m.len()); }
	    for i in 0..N {
		for j in 0..$n {
		    out.push(m[j*N + i]);
		}
	    }
	    out
	}
    }
}

#[macro_export]
macro_rules! flatten_matrix_raw {
    [$t:ty; $n:expr, $N:expr; $m:expr, $M:expr] => {
	|m: &$t| -> [f64; ($N-$n)*($M-$m)] {
	    let mut out = [NAN; ($N-$n)*($M-$m)];
	    let mut l = 0;
	    for i in $n..$N {
		for j in $m..$M {
		    out[l] = m[i][j];
		    l += 1;
		}
	    }
	    out
	}
    };
    [$n:expr, $N:expr; $m:expr, $M:expr] => { flatten_matrix_raw![[[f64; $M]; $N];$n,$N;$m,$M]; };
    ($N: expr, $M: expr) => { flatten_matrix_raw![0,$N;0,$M]; }
}

#[macro_export]
macro_rules! flatten_matrix {
    ($DIM_AX: expr, $DIM_RAD: expr) => {
        |m: &Matrix| -> [f64; ($DIM_RAD + 2) * $DIM_AX] {
            let mut out = [NAN; ($DIM_RAD + 2) * $DIM_AX];
            let mut l: usize = 0;
            for j in 0..$DIM_RAD + 2 {
                for i in 1..=$DIM_AX {
                    out[l] = m[i][j];
                    l += 1;
                }
            }
            out
        }
    };
}

#[macro_export]
macro_rules! flatten_tensor {
    ($DIM_AX: expr, $DIM_RAD: expr) => {
        |B: &KMatrix| -> [f64; $DIM_RAD * ($DIM_RAD + 2) * $DIM_AX] {
            let mut T_soil_tensor = [NAN; $DIM_RAD * ($DIM_RAD + 2) * $DIM_AX];
            let mut l: usize = 0;
            for i in 1..=$DIM_AX {
                for j in 1..=$DIM_RAD {
                    for k in 0..$DIM_RAD + 2 {
                        T_soil_tensor[l] = B[i][j][k];
                        l += 1;
                    }
                }
            }
            T_soil_tensor
        }
    };
}
