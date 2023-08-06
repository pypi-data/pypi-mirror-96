#![allow(non_snake_case)]
#![allow(clippy::many_single_char_names)]
#![allow(clippy::needless_range_loop)]
#![allow(clippy::too_many_arguments)]

use std::f64::consts::PI;
use std::f64::INFINITY;

pub mod error;
pub mod model;
pub mod numerics;
pub use model::{
    FluidProperties, GConeParameters, GlobalParameters, SoilLayerProperties, TBrineCalcMethod, DHE,
};
use numerics::{solve_tridiagonal, solve_vandermonde};

pub struct DHEField<'a, P> {
    pub sum_g: Vec<f64>,
    pub dg: Vec<f64>,
    pub dhe: &'a [DHECore<P>],
}

/// Low level parametrization of the DHE struct
#[derive(Debug)]
pub struct DHECore<P> {
    pub L: f64,
    pub R: f64,
    pub x: f64,
    pub y: f64,
    pub g: Vec<f64>,
    pub d_lambda_soil: Vec<f64>,
    pub n_steps: usize,
    pub L1_on: f64,
    pub pump_dependent_parameters: [TSoilParameters<P>; 2],
}

pub struct DHEState {
    pub Q: Vec<f64>,
    pub T_soil: Vec<f64>,
    pub T_U: Vec<f64>,
    pub T_sink: f64,
}

#[derive(Clone, Debug)]
pub struct TSoilParameters<P> {
    pub T_soil_tensor: Vec<f64>,
    pub L: Vec<f64>,
    pub T_brine_method: P,
}

pub struct TBrineDynamicParameters {
    pub n_sub_steps: u32,
    pub kappa_ax: f64,
    pub kappa_rad: Vec<f64>,
    pub lambda_brine: Vec<f64>,
}

pub struct TBrineStationaryParameters {
    pub kappa_brine: Vec<f64>,
    pub kappa_soil: Vec<f64>,
    pub L: Vec<f64>,
}
pub struct TBrineCalcMethodDynamic {}
pub struct TBrineCalcMethodStationary {}

pub trait TBrineMethod {
    fn refresh(
        &self,
        T_soil: &[f64],
        T_U: &mut [f64],
        Q_wall: &mut [f64],
        dim_ax: usize,
        T_sink: f64,
    ) -> f64;
}

#[derive(Clone)]
pub struct GFuncParametersCore {
    pub g_coefs: [f64; 6],
    pub u_min: f64,
    pub L: f64,
    pub go_const: f64,
}

pub trait BoundaryMethod {
    fn g_func(&self, t: &[f64], c_V_soil: &[f64], lambda_soil: &[f64], r: &[f64]) -> Vec<f64>;
}

pub struct CalcPOutputRefMut<'a> {
    pub T_sink: &'a mut [f64],
    pub T_source: &'a mut [f64],
    pub T_soil: &'a mut [f64],
}

pub trait Calculate {
    fn calculate_core_ref<'a, FTB: private::TBrineMethodFactory, G: BoundaryMethod>(
        &self,
        t: &[f64],
        P: &[f64],
        dhe: &[DHE],
        env: &GlobalParameters,
        g_method: &G,
        out: &mut [CalcPOutputRefMut<'a>],
    ) -> Result<(), error::Error>;
    fn calculate_ref<'a, G: BoundaryMethod>(
        &self,
        t: &[f64],
        P: &[f64],
        dhe: &[DHE],
        env: &GlobalParameters,
        g_method: &G,
        T_brine_method: TBrineCalcMethod,
        out: &mut [CalcPOutputRefMut<'a>],
    ) -> Result<(), error::Error> {
        match T_brine_method {
            TBrineCalcMethod::Dynamic => {
                self.calculate_core_ref::<TBrineCalcMethodDynamic, _>(t, P, dhe, env, g_method, out)
            }
            TBrineCalcMethod::Stationary => self
                .calculate_core_ref::<TBrineCalcMethodStationary, _>(t, P, dhe, env, g_method, out),
        }
    }
}

impl Calculate for model::CalculationMode {
    fn calculate_core_ref<'a, FTB: private::TBrineMethodFactory, G: BoundaryMethod>(
        &self,
        t: &[f64],
        P: &[f64],
        dhe: &[DHE],
        env: &GlobalParameters,
        g_method: &G,
        out: &mut [CalcPOutputRefMut<'a>],
    ) -> Result<(), error::Error> {
        match self {
            model::CalculationMode::P(mode) => {
                mode.calculate_core_ref::<FTB, _>(t, P, dhe, env, g_method, out)
            }
        }
    }
}

pub enum GParametersCore {
    GFunc(GFuncParametersCore),
    GCone(GConeParameters),
}

impl BoundaryMethod for GParametersCore {
    fn g_func(&self, t: &[f64], c_V_soil: &[f64], lambda_soil: &[f64], r: &[f64]) -> Vec<f64> {
        match self {
            GParametersCore::GFunc(p) => p.g_func(t, c_V_soil, lambda_soil, r),
            GParametersCore::GCone(p) => p.g_func(t, c_V_soil, lambda_soil, r),
        }
    }
}

impl Calculate for model::PCalculationMode {
    fn calculate_core_ref<'a, FTB: private::TBrineMethodFactory, G: BoundaryMethod>(
        &self,
        t: &[f64],
        P: &[f64],
        dhe: &[DHE],
        env: &GlobalParameters,
        g_method: &G,
        out: &mut [CalcPOutputRefMut<'a>],
    ) -> Result<(), error::Error> {
        calc_P::<FTB, _>(t, P, dhe, env, g_method, self.precision, out)
    }
}

/// Wraps calc_P_core (builds DHECore from DHE first)
pub fn calc_P<'a, FTB: private::TBrineMethodFactory, G: BoundaryMethod>(
    t: &[f64],
    P: &[f64],
    dhe: &[DHE],
    env: &GlobalParameters,
    g_method: &G,
    precision: f64,
    out: &mut [CalcPOutputRefMut<'a>],
) -> Result<(), error::Error> {
    let t_boundary_refresh = numerics::arange(
        t[0] + env.dt_boundary_refresh,
        t[t.len() - 1] + env.dt_boundary_refresh,
        env.dt_boundary_refresh,
    );
    let U_brine_on = dhe.iter().map(|d| d.brine_properties.c * d.Phi_m).sum();
    let U_brine: Vec<f64> = P
        .iter()
        .map(|_P| if *_P > 0. { U_brine_on } else { 0. })
        .collect();
    let statefull_dhe = dhe
        .iter()
        .map(|d| d.with_state::<_, _, FTB>(env, g_method, &t_boundary_refresh))
        .collect::<Result<Vec<_>, _>>()?;
    let (dhe_, mut dhe_states): (Vec<_>, Vec<_>) =
        statefull_dhe.into_iter().map(|t| (t.0, t.1)).unzip();
    let mut sum_Q0 = vec![0.; env.dim_ax];
    let mut Q_wall = vec![0.; env.dim_ax];
    calc_P_core(
        P,
        &U_brine,
        env.dim_ax,
        env.dim_rad,
        &dhe_,
        &mut dhe_states,
        &mut sum_Q0,
        &mut Q_wall,
        (env.dt_boundary_refresh / env.dt) as usize,
        precision,
        out,
    );
    Ok(())
}

/// Low level routine
/// @param U_brine U_brine = Phi_m * c_brine [W/K]
pub fn calc_P_core<'a, Prm: TBrineMethod>(
    P: &[f64],
    U_brine: &[f64],
    dim_ax: usize,
    dim_rad: usize,
    dhe: &[DHECore<Prm>],
    dhe_states: &mut [DHEState],
    sum_Q0: &mut [f64],
    Q_wall: &mut [f64],
    n_boundary_refresh: usize,
    precision: f64,
    out: &mut [CalcPOutputRefMut<'a>],
) {
    let n_DHE = dhe.len();
    let dim_t = P.len();
    let mut T_soil_old = vec![0.; dim_ax * (dim_rad + 2)];
    let mut T_U_old = vec![0.; 2 * dim_ax];
    let mut sum_Q0_old = vec![0.; dim_ax];
    let mut T0 = vec![0.; n_DHE * dim_ax];
    for k in 0..n_DHE {
        T0[k * dim_ax..(k + 1) * dim_ax]
            .clone_from_slice(&dhe_states[k].T_soil[dim_rad * dim_ax..(dim_rad + 1) * dim_ax]);
        dhe_states[k].T_sink = mean(&dhe_states[k].T_soil[dim_ax..2 * dim_ax]);
    }
    let mut N: usize = dim_t / n_boundary_refresh;
    if dim_t % n_boundary_refresh != 0 {
        N += 1
    };
    let chunk_size = std::cmp::min(n_boundary_refresh, dim_t);
    let dhe_field = DHEField::new(dhe, N, dim_ax);
    let mut chunk_pos: usize = 0;
    let mut chunk_pos_Q: usize = 0;
    let mut chunk_pos_T_soil: usize = 0;
    let chunk_size_T_soil = chunk_size * dim_ax * (dim_rad + 2);
    let mut _boundary_step = |chunk_pos,
                              chunk_pos_T_soil,
                              chunk_size: usize,
                              chunk_size_T_soil: usize,
                              dhe_states: &mut [DHEState],
                              sum_Q0: &mut [f64]| {
        for k in 0..n_DHE {
            boundary_step(
                &P[chunk_pos..chunk_pos + chunk_size],
                &U_brine[chunk_pos..chunk_pos + chunk_size],
                dim_ax,
                dim_rad,
                dhe[k].n_steps,
                dhe[k].L1_on * n_DHE as f64,
                &dhe[k].pump_dependent_parameters,
                &mut dhe_states[k].T_sink,
                &mut dhe_states[k].T_soil,
                &mut dhe_states[k].T_U,
                sum_Q0,
                Q_wall,
                &mut T_soil_old,
                &mut T_U_old,
                &mut sum_Q0_old,
                precision,
                &mut out[k].T_sink[chunk_pos..chunk_pos + chunk_size],
                &mut out[k].T_source[chunk_pos..chunk_pos + chunk_size],
                &mut out[k].T_soil[chunk_pos_T_soil..chunk_pos_T_soil + chunk_size_T_soil],
            );
        }
    };
    for n_chunk in 1..=dim_t / chunk_size {
        _boundary_step(
            chunk_pos,
            chunk_pos_T_soil,
            chunk_size,
            chunk_size_T_soil,
            dhe_states,
            sum_Q0,
        );
        chunk_pos += chunk_size;
        chunk_pos_Q += dim_ax;
        chunk_pos_T_soil += chunk_size_T_soil;

        for k in 0..n_DHE {
            let T_soil_boundary = &mut dhe_states[k].T_soil[dim_ax * (dim_rad + 1)..];
            for j in 0..dim_ax {
                dhe_states[k].Q[chunk_pos_Q + j] =
                    sum_Q0[j] / (dhe[k].n_steps * n_boundary_refresh) as f64;
                T_soil_boundary[j] = T0[k * dim_ax + j];
                sum_Q0[j] = 0.;
            }
            dhe_field.Delta_T_boundary(dhe_states, n_chunk, dim_ax, dim_rad);
        }
    }
    let rest_size = dim_t % chunk_size;
    if rest_size > 0 {
        _boundary_step(
            chunk_pos,
            chunk_pos_T_soil,
            rest_size,
            rest_size * dim_ax * (dim_rad + 2),
            dhe_states,
            sum_Q0,
        );
    }
}

pub struct StatefulDHE<P>(pub DHECore<P>, pub DHEState);

impl DHE {
    pub fn with_state<
        G: BoundaryMethod,
        TB: TBrineMethod,
        F: private::TBrineMethodFactory<TargetMethod = TB>,
    >(
        &self,
        env: &GlobalParameters,
        g_method: &G,
        t_boundary_refresh: &[f64],
    ) -> Result<StatefulDHE<TB>, String> {
        let dim_ax = env.dim_ax;
        let dim_rad = env.dim_rad;
        let dl = self.L / dim_ax as f64; // [m]
        let (c_V_soil, lambda_soil) = sample_soil_layers(&env.soil_layers, self.L, dim_ax)?;
        let R_domain = env.R - 0.5 * self.D_borehole;
        let r = r_grid(self.D, self.D_borehole, R_domain, dim_rad, env.Gamma);
        let rz = rz_grid(&r);

        let d_DHE_ref = 10.;
        let d_DHE_delta = 0.05;
        let q_drain = vec![0.; dim_ax];
        let (u_min, g_values) = g_poly(
            &self.T_soil_0_parameters.g_coefs,
            self.T_soil_0_parameters.d_DHE,
            d_DHE_ref,
            d_DHE_delta,
        )?;
        let T_soil = T_soil_0(
            env.t0,
            g_values,
            dim_ax,
            dl,
            &c_V_soil,
            &lambda_soil,
            &rz,
            env.soil_parameters.T_soil_mean,
            &q_drain,
            env.soil_parameters.T_grad,
            u_min,
        );
        let mut T_U = vec![0.; 2 * dim_ax];
        T_U[0..dim_ax].clone_from_slice(&T_soil[0..dim_ax]);
        for _a in 0..dim_ax {
            T_U[dim_ax + _a] = T_soil[dim_ax - 1 - _a];
        }
        let state = DHEState {
            T_U,
            T_soil,
            T_sink: 0.,
            Q: vec![0.; t_boundary_refresh.len() * dim_ax],
        };

        let U_brine = self.brine_properties.c * self.Phi_m;
        let alpha = alpha1(
            &self.brine_properties,
            self.Phi_m / self.brine_properties.rho,
            self.D,
            self.thickness,
        );

        let mut R1 = self.R1;
        let lambda_fill = self.fill_properties.lambda;
        let c_V_fill = self.fill_properties.c * self.fill_properties.rho;
        let lambda_brine = self.brine_properties.lambda;
        if R1 <= 0. {
            R1 = R_1(dl, &r, &rz, alpha, lambda_fill, self.Ra, self.Rb);
        }
        let R2 = R_2(dl, &r, &rz, lambda_fill, &lambda_soil, self.Ra, self.Rb);
        let L1_on = 1. / R1;
        let L1_off =
            1. / (R1 + (1. / alpha0(lambda_brine, self.D) - 1. / alpha) / (8. * PI * r[0] * dl));

        let (L_on, L_off) = L_pump(dl, &r, &rz, L1_on, L1_off, &R2, env.adiabat, &lambda_soil); // (dim_rad+1) x dim_ax

        // Heat capacity
        let C = C_matrix(dl, &r, c_V_fill, &c_V_soil);

        let n_steps = optimal_n_steps(
            &L_on,
            &C,
            dim_ax,
            dim_rad,
            env.dt,
            env.optimal_n_steps_multiplier,
        );
        let dt_step = env.dt / n_steps as f64;

        let C_brine = 2.
            * self.brine_properties.c
            * self.brine_properties.rho
            * PI
            * 0.25
            * self.D
            * self.D
            * dl; // J/K
        let Lm_min = C_brine / f64::max(U_brine, L1_on);
        let n_steps_on = (env.n_steps_0 as f64 * dt_step / Lm_min) as usize + 1;
        let n_steps_off = (env.n_steps_0 as f64 * dt_step / C_brine * L1_off) as usize + 1;
        let L_on_0: Vec<f64> = (0..dim_ax).map(|a_| L_on[a_ * (dim_rad + 1)]).collect();
        let L_off_0: Vec<f64> = (0..dim_ax).map(|a_| L_off[a_ * (dim_rad + 1)]).collect();

        let T_brine_method_on = F::build(dt_step, C_brine, &L_on_0, n_steps_on, U_brine);
        let T_brine_method_off = F::build(dt_step, C_brine, &L_off_0, n_steps_off, 0.);
        Ok(StatefulDHE(
            DHECore {
                x: self.x,
                y: self.y,
                L: self.L,
                R: env.R,
                L1_on,
                n_steps,
                d_lambda_soil: lambda_soil.iter().map(|l| l * dl).collect(),
                g: g_method.g_func(t_boundary_refresh, &c_V_soil, &lambda_soil, &[env.R]),
                pump_dependent_parameters: [
                    TSoilParameters {
                        L: L_off_0,
                        T_soil_tensor: T_soil_evolution(&L_off, &C, dt_step, dim_ax, dim_rad),
                        T_brine_method: T_brine_method_off,
                    },
                    TSoilParameters {
                        L: L_on_0,
                        T_soil_tensor: T_soil_evolution(&L_on, &C, dt_step, dim_ax, dim_rad),
                        T_brine_method: T_brine_method_on,
                    },
                ],
            },
            state,
        ))
    }
}

/// U1_on = L1_on * n_DHE
fn boundary_step<Prm: TBrineMethod>(
    P: &[f64],
    U_brine: &[f64],
    dim_ax: usize,
    dim_rad: usize,
    n_steps: usize,
    U1_on: f64,
    pump_dependent_parameters: &[TSoilParameters<Prm>; 2],
    T_sink_p: &mut f64,
    T_soil: &mut [f64],
    T_U: &mut [f64],
    sum_Q0: &mut [f64],
    Q_wall: &mut [f64],
    T_soil_old: &mut [f64],
    T_U_old: &mut [f64],
    sum_Q0_old: &mut [f64],
    precision: f64,
    out_T_sink: &mut [f64],
    out_T_source: &mut [f64],
    out_T_soil: &mut [f64],
) {
    let n_boundary_refresh = P.len();
    let mut pump_is_on: bool;
    let mut T_source: f64;
    let mut T_sink_ref: f64;
    let mut T_sink = *T_sink_p;
    let size_T_soil = dim_ax * (dim_rad + 2);

    for i in 0..n_boundary_refresh {
        pump_is_on = U_brine[i] > 0.;
        if pump_is_on {
            T_sink -= P[i] * (1. / U1_on + 1. / U_brine[i]);
            T_soil_old.clone_from_slice(T_soil);
            T_U_old.clone_from_slice(T_U);
            sum_Q0_old.clone_from_slice(sum_Q0);
        }
        T_source = soil_step(
            T_soil,
            T_sink,
            sum_Q0,
            dim_ax,
            dim_rad,
            n_steps,
            Q_wall,
            T_U,
            &pump_dependent_parameters[pump_is_on as usize],
        );
        if pump_is_on {
            T_sink = T_source - P[i] / U_brine[i];
            T_sink_ref = T_sink + 2. * precision;
            while f64::abs(T_sink - T_sink_ref) > precision {
                T_soil.clone_from_slice(T_soil_old);
                T_U.clone_from_slice(T_U_old);
                sum_Q0.clone_from_slice(sum_Q0_old);
                T_source = soil_step(
                    T_soil,
                    T_sink,
                    sum_Q0,
                    dim_ax,
                    dim_rad,
                    n_steps,
                    Q_wall,
                    T_U,
                    &pump_dependent_parameters[pump_is_on as usize],
                );
                T_sink_ref = T_sink;
                T_sink = T_source - P[i] / U_brine[i];
                if f64::abs(T_sink) > 100. {
                    T_sink = -1.;
                    T_sink_ref = T_sink + 2. * precision;
                }
            }
        } else {
            T_sink = T_soil[dim_ax + 1];
            T_source = T_sink;
        }
        out_T_sink[i] = T_sink;
        out_T_source[i] = T_source;

        out_T_soil[i * size_T_soil..(i + 1) * size_T_soil].clone_from_slice(T_soil);
    }
    *T_sink_p = T_sink;
}

pub const DEFAULT_GO_CONST: f64 = 6.84;

impl<'a, P> DHEField<'a, P> {
    pub fn new(dhe: &'a [DHECore<P>], dim_t: usize, dim_ax: usize) -> Self {
        let sum_g = (0..dim_t * dim_ax)
            .map(|l| dhe.iter().map(|d| d.g[l]).sum())
            .collect();
        DHEField {
            dg: DHE_geometry(&dhe),
            sum_g,
            dhe,
        }
    }

    /// @brief Superposition of boundary conditions
    /// @param d_lamda_soil lambda_soil * dl. shape: (dim_ax,) or ()
    /// @param q Heat loss. shape: (dim_t+1, dim_ax)
    /// @param g Values of the g function per time and height. shape: (dim_t, dim_ax)
    pub fn Delta_T_boundary(
        &self,
        states: &mut [DHEState],
        dim_t: usize,
        dim_ax: usize,
        dim_rad: usize,
    ) {
        let mut Delta_T: f64;
        let sum_g = &self.sum_g;
        let dg = &self.dg;
        let dhe = &self.dhe;

        for j in 0..dim_ax {
            Delta_T = 0.;
            for k in 0..dhe.len() {
                let T_soil_boundary = &mut states[k].T_soil[dim_ax * (dim_rad + 1)..];
                for i in 0..dim_t {
                    Delta_T += (sum_g[i * dim_ax + j] - dg[k])
                        * (-states[k].Q[(dim_t - i) * dim_ax + j]
                            + states[k].Q[(dim_t - 1 - i) * dim_ax + j]);
                }
                T_soil_boundary[k * dim_ax + j] +=
                    Delta_T / (2. * std::f64::consts::PI * dhe[k].d_lambda_soil[j]);
            }
        }
    }
}

/// @brief Encodes the distances between the single
///        DHEs into an array out_dg for use in
///        Delta_T_boundary
///
/// out_dg[k] = \sum_{l=0, l\neq k}^n_DHE log(d(k,l)/r[l]), where
/// d(k, l) is the distance between dhe k and dhe l.
///
/// g_eff[k] = g[k] + \sum_{l=0, l\neq k}^n_DHE g[l] - log(d(k, l)/r[l])
///          = \sum_{l=0}^n_DHE g[l] - \sum_{l=0, l\neq k}^n_DHE log(d(k, l)/r[l])
fn DHE_geometry<P>(dhe: &[DHECore<P>]) -> Vec<f64> {
    let n_DHE = dhe.len();
    let mut out = vec![0.; n_DHE];
    for k in 0..n_DHE {
        for l in 0..n_DHE {
            if l == k {
                continue;
            }
            out[k] += f64::ln(f64::hypot(dhe[k].x - dhe[l].x, dhe[k].y - dhe[l].y) / dhe[l].R);
        }
    }
    out
}

impl TBrineMethod for TBrineDynamicParameters {
    /// @param Q_wall passed only to prevent reallocating [W/m]
    /// @param U_brine U_brine = Phi c_V_brine
    /// @param dC_brine dC_brine = 2 c_V_brine pi r_DHE^2 dl
    /// @param kappa_ax kappa_ax = U_brine / dC_brine/// dt_step
    /// @param kappa_rad kappa_rad = lambda_brine/// dt / dC_brine
    /// @param lambda_brine lambda_brine = 0.5/// L / n_sub_steps
    fn refresh(
        &self,
        T_soil: &[f64],
        T_U: &mut [f64],
        Q_wall: &mut [f64],
        dim_ax: usize,
        T_sink: f64,
    ) -> f64 {
        // dt_step = dt / n_sub_steps;
        let mut T_out: f64 = 0.;
        // L0mcpdt = U_brine / dC_brine * dt_step;
        // lambda_brine = 0.5 * L / n_sub_steps;
        // L1mcpdt = lambda_brine * dt / dC_brine;
        for (Q, T) in Q_wall.iter_mut().zip(T_soil) {
            *Q = 2. * f64::from(self.n_sub_steps) * *T;
        }
        let kappa_ax = self.kappa_ax;
        let kappa_rad = &self.kappa_rad;
        let mut T_prev;
        let mut T_current;
        for _step in 0..self.n_sub_steps {
            T_prev = T_sink;
            for i in 0..dim_ax {
                T_current = T_U[i];
                T_current +=
                    (T_prev - T_current) * kappa_ax + (T_soil[i] - T_current) * kappa_rad[i];
                T_prev = T_current;
                T_U[i] = T_current;
                Q_wall[i] -= T_prev;
            }
            for i in 0..dim_ax {
                T_current = T_U[dim_ax + i];
                T_current += (T_prev - T_current) * kappa_ax
                    + (T_soil[dim_ax - 1 - i] - T_current) * kappa_rad[dim_ax - 1 - i];
                T_prev = T_current;
                T_U[dim_ax + i] = T_current;
                Q_wall[dim_ax - 1 - i] -= T_prev;
            }
            T_out += T_U[2 * dim_ax - 1];
        }
        for i in 0..dim_ax {
            Q_wall[i] *= self.lambda_brine[i];
        }
        T_out /= f64::from(self.n_sub_steps);
        T_out
    }
}

mod private {
    pub trait TBrineMethodFactory {
        type TargetMethod: super::TBrineMethod;
        fn build(
            dt: f64,
            dC_brine: f64,
            L: &[f64],
            n_sub_steps: usize,
            U_brine: f64,
        ) -> Self::TargetMethod;
    }
}

impl private::TBrineMethodFactory for TBrineCalcMethodDynamic {
    type TargetMethod = TBrineDynamicParameters;
    fn build(
        dt: f64,
        dC_brine: f64,
        L: &[f64],
        n_sub_steps: usize,
        U_brine: f64,
    ) -> Self::TargetMethod {
        let dt_step = dt / n_sub_steps as f64;
        let lambda_brine: Vec<f64> = L.iter().map(|l| 0.5 * l / n_sub_steps as f64).collect();
        let kappa_rad = lambda_brine.iter().map(|l| l * dt / dC_brine).collect();
        TBrineDynamicParameters {
            kappa_ax: U_brine / dC_brine * dt_step,
            kappa_rad,
            lambda_brine,
            n_sub_steps: n_sub_steps as u32,
        }
    }
}

impl TBrineMethod for TBrineStationaryParameters {
    /// @brief Stationary T_brine method
    ///
    /// @param U_brine U_brinemcpdt = U_brine / U_brine/// dt2
    /// @param T_U shape (2, n)
    /// T_U[0] is T_down, T_U[1] is T_up
    /// kappa_soil = L / (L + 2*U_brine)
    /// kappa_brine = U_brine / (0.5/// L + U_brine)
    fn refresh(
        &self,
        T_soil: &[f64],
        T_U: &mut [f64],
        Q_wall: &mut [f64],
        dim_ax: usize,
        T_sink: f64,
    ) -> f64 {
        let kappa_soil = &self.kappa_soil;
        let kappa_brine = &self.kappa_brine;
        T_U[0] = kappa_soil[0] * T_soil[0] + kappa_brine[0] * T_sink;
        for i in 1..dim_ax {
            T_U[i] = kappa_soil[i] * T_soil[i] + kappa_brine[i] * T_U[i - 1];
        }
        for i in 0..dim_ax {
            T_U[dim_ax + i] = kappa_soil[dim_ax - 1 - i] * T_soil[dim_ax - 1 - i]
                + kappa_brine[dim_ax - 1 - i] * T_U[dim_ax + i - 1];
        }
        for i in 0..dim_ax {
            Q_wall[i] = (2. * T_soil[i] - T_U[i] - T_U[2 * dim_ax - 1 - i]) * 0.5 * self.L[i];
        }
        T_U[2 * dim_ax - 1]
    }
}

impl private::TBrineMethodFactory for TBrineCalcMethodStationary {
    type TargetMethod = TBrineStationaryParameters;
    fn build(
        _dt: f64,
        _dC_brine: f64,
        L: &[f64],
        _n_sub_steps: usize,
        U_brine: f64,
    ) -> Self::TargetMethod {
        let kappa_soil = L.iter().map(|l| l / (l + 2. * U_brine)).collect();
        let kappa_brine = L.iter().map(|l| U_brine / (0.5 * l + U_brine)).collect();
        TBrineStationaryParameters {
            kappa_soil,
            kappa_brine,
            L: L.to_vec(),
        }
    }
}

impl BoundaryMethod for GFuncParametersCore {
    /// @brief Boundary condition with g function
    ///
    /// @param t Array of time [s]
    /// @param c_V_soil Volume specific heat of soil
    /// @param L Length of borehole
    /// @param r Radius at which to calculate boundary conditions
    fn g_func(&self, t: &[f64], c_V_soil: &[f64], lambda_soil: &[f64], r: &[f64]) -> Vec<f64> {
        let mut u: f64;
        let mut g: f64;
        let mut go: f64;
        let GFuncParametersCore {
            L,
            u_min,
            go_const,
            g_coefs,
        } = *self;
        let dim_ax = c_V_soil.len();
        let dim_rad = r.len();
        let dim_t = t.len();
        let mut out_g = vec![0.; dim_t * dim_ax * dim_rad];
        let mut ts = vec![0.; dim_ax];
        let mut log_r = vec![0.; dim_rad];
        for i in 0..dim_ax {
            ts[i] = L * L / (9. * lambda_soil[i]) * c_V_soil[i];
        }
        for j in 0..dim_rad {
            log_r[j] = f64::ln(r[j] / (L * 0.0005));
        }
        let mut l: usize = 0;
        for k in 0..dim_t {
            for i in 0..dim_ax {
                u = f64::ln(t[k] / ts[i]);
                if u > 2.5 {
                    u = 2.5;
                }
                go = 0.5 * u + go_const;
                if u < u_min {
                    g = go;
                } else {
                    g = g_coefs[0]
                        + u * (g_coefs[1]
                            + u * (g_coefs[2]
                                + u * (g_coefs[3] + u * (g_coefs[4] + u * g_coefs[5]))));
                }
                if u < -2. && go - 0.3 > g {
                    g = go;
                }
                for j in 0..dim_rad {
                    out_g[l] = g - log_r[j];
                    l += 1;
                }
            }
        }
        out_g
    }
}
impl BoundaryMethod for GConeParameters {
    /// @brief Boundary condition according to cone formula by Werner
    fn g_func(&self, t: &[f64], c_V_soil: &[f64], lambda_soil: &[f64], r: &[f64]) -> Vec<f64> {
        let mut u: f64;
        let mut _u: f64;
        let mut W: f64;
        let mut delta: f64;
        let mut fac: u64;
        let mut n: u64;
        let mut sign: i8;
        let dim_ax = c_V_soil.len();
        let dim_rad = r.len();
        let dim_t = t.len();
        let mut out_g = vec![0.; dim_t * dim_ax * dim_rad];
        let mut u0 = vec![0.; dim_ax];
        let mut rr = vec![0.; dim_rad];
        let mut keep_going: bool;
        for j in 0..dim_rad {
            rr[j] = r[j] * r[j];
        }
        for i in 0..dim_ax {
            u0[i] = c_V_soil[i] / (4. * lambda_soil[i]);
        }
        let mut l: usize = 0;
        for k in 0..dim_t {
            for i in 0..dim_ax {
                for j in 0..dim_rad {
                    u = u0[i] * rr[j] / t[k];
                    if u > 1. {
                        W = 0.;
                    } else {
                        W = -0.5772 - f64::ln(u) + u;
                        n = 1;
                        fac = 1;
                        sign = 1;
                        _u = u;
                        keep_going = true;
                        while keep_going {
                            sign = -sign;
                            _u *= u;
                            n += 1;
                            fac *= n;
                            delta = _u / (fac * n) as f64;
                            keep_going = delta > 0.01 * f64::abs(W);
                            W += sign as f64 * delta;
                        }
                        W *= 0.5;
                    }
                    out_g[l] = W;
                    l += 1;
                }
            }
        }
        out_g
    }
}

/// @param U_brine U_brine = cp_brine * Phi_m / n_DHE
/// @param T_soil shape: (dim_rad+2, dim_ax)
pub fn soil_step<P: TBrineMethod>(
    T_soil: &mut [f64],
    T_sink: f64,
    sum_Q0: &mut [f64],
    dim_ax: usize,
    dim_rad: usize,
    n_steps: usize,
    Q_wall: &mut [f64],
    T_U: &mut [f64],
    pump_dependent_parameters: &TSoilParameters<P>,
) -> f64 {
    let mut T_source = 0.;
    for _n in 0..n_steps {
        // Calculate brine Temperature
        T_source += pump_dependent_parameters.T_brine_method.refresh(
            &T_soil[dim_ax..],
            T_U,
            Q_wall,
            dim_ax,
            T_sink,
        );
        for i in 0..dim_ax {
            T_soil[i] = T_soil[dim_ax + i] - Q_wall[i] / pump_dependent_parameters.L[i];
            sum_Q0[i] += Q_wall[i];
        }
        // Update soil temperature
        T_soil_refresh(
            T_soil,
            &pump_dependent_parameters.T_soil_tensor,
            dim_ax,
            dim_rad,
        );
    }
    T_source /= n_steps as f64;
    T_source
}

/// @param T_soil [dim_rad+2, dim_ax]
/// @param T_soil_tensor [dim_ax, dim_rad, dim_rad+2]
/// T'_ia = sum_k TT_aik T_ka
pub fn T_soil_refresh(T_soil: &mut [f64], T_soil_tensor: &[f64], dim_ax: usize, dim_rad: usize) {
    let s1 = dim_rad + 2;
    let s0 = dim_rad * s1;
    let mut x = vec![0.0; dim_rad];
    for a_ in 0..dim_ax {
        for i in 0..dim_rad {
            x[i] = 0.;
            for k in 0..dim_rad + 2 {
                x[i] += T_soil_tensor[s0 * a_ + s1 * i + k] * T_soil[dim_ax * k + a_];
            }
        }
        for i in 0..dim_rad {
            T_soil[dim_ax * (i + 1) + a_] = x[i];
        }
    }
}

fn mean(x: &[f64]) -> f64 {
    x.iter().sum()
}

/// Returns B such that
/// T_new[.., 1..-1] = B T_old
/// If (dim_rad+2, dim_ax) is the shape of T_old, then
/// B has shape (dim_ax, dim_rad, dim_rad+2)
///
///  B is determined such that
///  sum_l A_arl T_new[.., 1..-1]_al = sum_l F_arl T_old_al
///        / * * 0 \        / * | * * 0 | 0 \
///  A_a = | * * * |  F_a = | 0 | * * * | 0 |
///        \ 0 * * /        \ 0 | 0 * * | * /
pub fn T_soil_evolution(
    L: &[f64],
    C: &[f64],
    dt_step: f64,
    dim_ax: usize,
    dim_rad: usize,
) -> Vec<f64> {
    let _LC = |L: &[f64], C: &[f64], dt: f64| {
        // L: dim_ax * (dim_rad + 1)
        // C: dim_ax * dim_rad
        let mut out_diag = vec![0.; dim_ax * dim_rad];
        let mut out_offdiag = vec![0.; dim_ax * (dim_rad - 1)];
        let s = dim_rad;
        for a_ in 0..dim_ax {
            for r_ in 0..dim_rad {
                out_diag[a_ * s + r_] = 2. * C[a_ * dim_rad + r_]
                    + dt * (L[a_ * (dim_rad + 1) + r_ + 1] + L[a_ * (dim_rad + 1) + r_]);
            }
        }
        let s = dim_rad - 1;
        for a_ in 0..dim_ax {
            for r_ in 0..dim_rad - 1 {
                out_offdiag[a_ * s + r_] = -dt * L[a_ * (dim_rad + 1) + r_ + 1];
            }
        }
        (out_diag, out_offdiag)
    };
    let (A_diag, A_offdiag) = _LC(L, C, dt_step);
    let (F_diag, F_offdiag) = _LC(L, C, -dt_step);
    let mut TT = vec![0.; dim_ax * (dim_rad + 2) * dim_rad];
    let s0 = dim_rad * (dim_rad + 2);
    for a_ in 0..dim_ax {
        let mut F = vec![0.; (dim_rad + 2) * dim_rad];
        // F_i00 = 2 dt L_i0
        F[0] = 2. * dt_step * L[a_ * (dim_rad + 1)];
        // F_i(dim_rad)(dim_rad+2) = 2 dt L_i(dim_rad)
        F[s0 - 1] = 2. * dt_step * L[(a_ + 1) * (dim_rad + 1) - 1];
        for r_ in 0..dim_rad {
            F[(r_ + 1) * dim_rad + r_] = F_diag[dim_rad * a_ + r_];
        }
        for r_ in 0..dim_rad - 1 {
            F[(r_ + 1) * dim_rad + r_ + 1] = F_offdiag[(dim_rad - 1) * a_ + r_];
            F[(r_ + 2) * dim_rad + r_] = F_offdiag[(dim_rad - 1) * a_ + r_];
        }
        solve_tridiagonal(
            &A_diag[a_ * dim_rad..(a_ + 1) * dim_rad],
            &A_offdiag[a_ * (dim_rad - 1)..(a_ + 1) * (dim_rad - 1)],
            &A_offdiag[a_ * (dim_rad - 1)..(a_ + 1) * (dim_rad - 1)],
            &mut F,
            dim_rad + 2,
        )
        .unwrap();
        // Transpose F into TT
        for j in 0..dim_rad {
            for k in 0..dim_rad + 2 {
                TT[a_ * s0 + j * (dim_rad + 2) + k] = F[k * dim_rad + j];
            }
        }
    }
    TT
}

/// Given dim_l layers :param layers: of soil with parameters
/// (constant across single layers).
/// Calculate values for a number of dim_ax equispaced layers of total thickness
/// L_DHE. The output layers values are taken to be the length averages of the
/// input layer values over the ranges of the output layers.
fn sample_soil_layers(
    layers: &[SoilLayerProperties],
    L_DHE: f64,
    dim_ax: usize,
) -> Result<(Vec<f64>, Vec<f64>), String> {
    let mut L;
    let mut layers_iter = layers.iter();
    let mut L0_layer = 0.;
    let mut layer = layers_iter.next().ok_or("Empty layers!")?;
    let mut d_layer = layer.d;
    let mut L1_layer = layer.d;
    let mut c_V_layer = 0.;
    let mut lambda_layer = 0.;
    let mut c_V = vec![0.; dim_ax];
    let mut lambda = vec![0.; dim_ax];
    let d_L = L_DHE / dim_ax as f64;
    for i in 0..dim_ax {
        L = (i + 1) as f64 * L_DHE / dim_ax as f64;
        while L1_layer < L {
            c_V_layer += layer.c * layer.rho * d_layer;
            lambda_layer += layer.lambda * d_layer;
            if let Some(l) = layers_iter.next() {
                layer = l;
                d_layer = l.d;
            } else {
                d_layer = INFINITY;
            }
            L0_layer = L1_layer;
            L1_layer += d_layer;
        }
        c_V_layer += layer.c * layer.rho * (L - L0_layer);
        lambda_layer += layer.lambda * (L - L0_layer);
        c_V[i] = c_V_layer / d_L;
        lambda[i] = lambda_layer / d_L;
        c_V_layer = 0.;
        lambda_layer = 0.;
        d_layer -= L - L0_layer;
        L0_layer = L;
    }
    Ok((c_V, lambda))
}

/// Determine optimal value for n_steps
pub fn optimal_n_steps(
    L: &[f64],
    C: &[f64],
    dim_ax: usize,
    dim_rad: usize,
    dt: f64,
    c: f64,
) -> usize {
    let mut dt_min = C[0] / L[0];
    let mut x;
    // L: dim_ax * (dim_rad+1), C: dim_ax * dim_rad
    for (i, j) in &[(0, 0), (0, 1), (1, 1)] {
        for a_ in 0..dim_ax {
            x = C[a_ * dim_rad + i] / L[a_ * (dim_rad + 1) + j];
            if x < dt_min {
                dt_min = x;
            }
        }
    }
    let out = (c * dt / dt_min) as usize;
    if out == 0 {
        1
    } else {
        out
    }
}

/// Resistance R1 in bore hole
pub fn R_1(dl: f64, r: &[f64], rz: &[f64], alpha: f64, lambda_fill: f64, Ra: f64, Rb: f64) -> f64 {
    if Ra > 0. && Rb > 0. {
        return Ra / (4. * dl);
    }
    if Rb > 0. {
        return Rb / dl - 1. / (2. * PI * dl * lambda_fill) * f64::ln(r[1] / rz[1]);
    }
    (1. / (alpha * r[0]) + f64::ln((r[1] - rz[1]) / r[0]) / lambda_fill) / (8. * PI * dl)
}

/// Resistance R2 in bore hole
pub fn R_2(
    dl: f64,
    r: &[f64],
    rz: &[f64],
    lambda_fill: f64,
    lambda_soil: &[f64],
    Ra: f64,
    Rb: f64,
) -> Vec<f64> {
    if Ra > 0. && Rb > 0. {
        return lambda_soil
            .iter()
            .map(|lambda| (Rb - 0.25 * Ra) / dl + f64::ln(rz[2] / r[1]) / (2. * PI * dl * lambda))
            .collect();
    }
    lambda_soil
        .iter()
        .map(|lambda| {
            (f64::ln(r[1] / rz[1]) / lambda_fill + f64::ln(rz[2] / r[1]) / lambda) / (2. * PI * dl)
        })
        .collect()
}

/// Pump on / off
pub fn L_pump(
    dl: f64,
    r: &[f64],
    rz: &[f64],
    L1_on: f64,
    L1_off: f64,
    R2: &[f64],
    adiabat: f64,
    lambda_soil: &[f64],
) -> (Vec<f64>, Vec<f64>) {
    let dim_ax = lambda_soil.len();
    let dim_r = r.len(); // r.len = dim_rad + 1
    let mut L_on = vec![0.; dim_ax * dim_r];
    let mut L_off = vec![0.; dim_ax * dim_r];
    for a_ in 0..dim_ax {
        L_on[a_ * dim_r] = L1_on;
        L_off[a_ * dim_r] = L1_off;
        L_on[a_ * dim_r + 1] = 1. / R2[a_];
        L_on[(a_ + 1) * dim_r - 1] = (1. - adiabat) * 2. * PI * dl * lambda_soil[a_]
            / f64::ln(r[r.len() - 1] / rz[r.len() - 1]);
        for r_ in 2..dim_r - 1 {
            L_on[a_ * dim_r + r_] = 2. * PI * dl * lambda_soil[a_] / f64::ln(rz[r_ + 1] / rz[r_]);
        }
        for r_ in 1..dim_r {
            L_off[a_ * dim_r + r_] = L_on[a_ * dim_r + r_];
        }
    }
    (L_on, L_off)
}

pub fn C_matrix(dl: f64, r: &[f64], c_V_fill: f64, c_V_soil: &[f64]) -> Vec<f64> {
    let dim_rad = r.len() - 1;
    let dim_ax = c_V_soil.len();
    let mut C = vec![0.; dim_ax * dim_rad];
    for a_ in 0..dim_ax {
        C[a_ * dim_rad] = PI * c_V_fill * (r[1] * r[1] - 4. * r[0] * r[0]) * dl;
        for r_ in 1..dim_rad {
            C[a_ * dim_rad + r_] = PI * dl * c_V_soil[a_] * (r[r_ + 1] * r[r_ + 1] - r[r_] * r[r_]);
        }
    }
    C
}

/// :param R: Domain of computation
/// :param Gamma: Grid parameter
pub fn r_grid(D_DHE: f64, D_borehole: f64, R: f64, dim_rad: usize, Gamma: f64) -> Vec<f64> {
    let mut r = vec![0.; dim_rad + 1];
    r[0] = 0.5 * D_DHE;
    r[1] = 0.5 * D_borehole;
    let c = R * (1. - Gamma) / (1. - Gamma.powi(dim_rad as i32 - 1));
    let mut x = 0.;
    let mut Gamma_p = 1.;
    for i in 2..r.len() {
        x += Gamma_p;
        Gamma_p *= Gamma;
        r[i] = r[1] + c * x;
    }
    r
}

pub fn rz_grid(r: &[f64]) -> Vec<f64> {
    let l = r.len() + 1;
    let mut rz = vec![0.; l];
    for i in 1..r.len() {
        rz[i] = f64::sqrt(0.5 * (r[i] * r[i] + r[i - 1] * r[i - 1]));
    }
    rz[0] = r[0];
    rz[l - 1] = r[r.len() - 1];
    rz
}

/// Heat transfer if pump is off
pub fn alpha0(lambda_brine: f64, D: f64) -> f64 {
    2. * lambda_brine / (D * (1. - f64::sqrt(0.5)))
}

/// Heat transfer brine backfill, when pump is on
/// :param thickness_DHE: Thickness DHE pipe
#[allow(clippy::useless_let_if_seq)]
pub fn alpha1(brine_properties: &FluidProperties, Phi: f64, D_DHE: f64, thickness_DHE: f64) -> f64 {
    let c_V_brine = brine_properties.c * brine_properties.rho;
    let nu_brine = brine_properties.nu;
    let lambda_brine = brine_properties.lambda;
    let Di = D_DHE - 2. * thickness_DHE;
    let v = 2. * Phi / (Di * Di) / PI;
    let Re = v * Di / nu_brine; // Reynolds number
    let Pr = nu_brine * c_V_brine / lambda_brine; // Prandtl number
    let Pr_3 = Pr.cbrt();
    //  Xi: pressure loss coefficient by Petukhov (1970)
    let Xi = 1. / 1.82 * f64::ln(Re * Re / f64::ln(10.) - 1.64);
    //  Stanton number by Petukhov (1970), valid for at turbulent speed
    let K1 = 1. + 27.2 * Xi / 8.;
    let K2 = 11.7 + 1.8 / Pr_3;
    let St = Xi / 8. / (K1 + K2 * f64::sqrt(Xi / 8.) * (Pr_3 * Pr_3 - 1.)); // Stanton number
                                                                            //  Stanton number by Petukhov at the border turbulence/transition zone
    let Xi0 = 0.031437;
    let K10 = 1.106886;
    let ST0 = Xi0 / 8. / (K10 + K2 * f64::sqrt(Xi0 / 8.) * (Pr_3 * Pr_3 - 1.));
    let Nu0 = ST0 * 10000. * Pr; // Nusselt number on transition turbulence/transition zone
    let Nu_turbulent = St * Re * Pr; // Nusselt number for turbulent zone
    let Nu_laminar = 4.36; // Nusselt number for laminar zone
    let mut Nu = 0.;
    if Re >= 10000. {
        Nu = Nu_turbulent;
    } // turbulent
    if Re <= 2300. {
        Nu = Nu_laminar; // laminar
    }
    // Transition zone laminar/turbulent
    else if Re < 10000. {
        Nu = Nu_laminar
            * f64::exp(f64::ln(Nu0 / Nu_laminar) / f64::ln(10000. / 2300.) * f64::ln(Re / 2300.));
    }
    Nu * lambda_brine / Di
}

pub fn g_poly(
    g: &[f64; 5],
    d_DHE: f64,
    d_DHE_ref: f64,   /* = 10 */
    d_DHE_delta: f64, /* = 0.05*/
) -> Result<(f64, [f64; 6]), String> {
    let mut g = *g;
    if f64::abs(d_DHE - d_DHE_ref) > d_DHE_delta {
        // Extrapolation of the g function
        let BH = d_DHE / d_DHE_ref;
        if BH < 0.4 {
            return Err(String::from("BH out of bounds"));
        }
        let ExA = g[4] - 6.29;
        let ExB = -f64::ln((g[2] - 6.29) / (g[4] - 6.6)) / 27.;
        let g0 = [4.82, 5.69, 6.29, 6.57, 6.6];
        let g_exp = [343., 125., 27., 1., 0.];
        for i in 0..g0.len() {
            g[i] = g0[i] + f64::max(0., ExA / BH * f64::exp(-BH * ExB * g_exp[i]));
        }
        // e Extrapolation g-Function
    }
    // Calculates g function from 4 sampling points g1,g2,g3,g4
    const N_X: usize = 6;
    let x: [f64; N_X] = [
        -4.,
        -2.,
        0.,
        2.5,
        3.,
        f64::min(-4.5, -4. - (g[0] - 4.82) / 2.),
    ];
    let mut y = [
        g[0],
        g[1],
        g[2],
        g[3],
        g[4] * 0.99,
        (f64::ln(0.5 / 0.0005) + 0.5 * x[5]) * 0.95,
    ];
    y[3] = (y[3] + y[4]) / 2. * 0.99;
    let u_min = f64::max(x[5] + 0.5, -6.);
    let mut out = [0.; 6];
    solve_vandermonde(&x, &y, N_X, &mut out);
    Ok((u_min, out))
}

/// :param T_grad: Gradient of Temperature axial [K/m]
/// :q_drain: Heat drained par layer. Shape: (dim_ax,)
///
/// :return: numpy array of shape (dim_rad + 2, dim_ax)
pub fn T_soil_0(
    t0: f64,
    g_coefs: [f64; 6],
    dim_ax: usize,
    dl: f64,
    c_V_soil: &[f64],
    lambda_soil: &[f64],
    rz: &[f64],
    T_soil: f64,
    q_drain: &[f64],
    T_grad: f64, /* = 0.03*/
    u_min: f64,
) -> Vec<f64> {
    let dim_r = rz.len();
    let mut Rq = vec![0.; dim_ax * rz.len()];
    if t0 != 0. {
        let g = GFuncParametersCore {
            g_coefs,
            L: dim_ax as f64 * dl,
            go_const: 6.907755,
            u_min,
        }
        .g_func(&[t0], c_V_soil, lambda_soil, rz);
        for r_ in 0..dim_r {
            for a_ in 0..dim_ax {
                Rq[r_ * dim_ax + a_] = g[a_ * dim_r + r_] / (2. * PI * lambda_soil[a_]);
            }
        }
    }
    let mut out = vec![0.; dim_r * dim_ax];
    let mut l = 0;
    for r_ in 0..dim_r {
        for a_ in 0..dim_ax {
            out[l] =
                T_soil + T_grad * dl * (a_ as f64 + 0.5) - Rq[r_ * dim_ax + a_] * q_drain[a_] / dl;
            l += 1;
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::{sample_soil_layers, SoilLayerProperties};
    #[test]
    fn test_sample_soil_layers() {
        let soil_layers = [
            SoilLayerProperties {
                d: 1.,
                rho: 3.,
                c: 3.,
                lambda: 0.,
            },
            SoilLayerProperties {
                d: 3.,
                rho: 2.,
                c: 3.,
                lambda: 0.,
            },
            SoilLayerProperties {
                d: 2.,
                rho: 1.,
                c: -1.,
                lambda: 0.,
            },
            SoilLayerProperties {
                d: 1.,
                rho: 3.,
                c: 3.,
                lambda: 0.,
            },
        ];

        let (c_V, lambda) = sample_soil_layers(&soil_layers, 6., 3).unwrap();
        assert_eq!(c_V, vec![7.5, 6., -1.]);
        assert_eq!(lambda, vec![0., 0., 0.]);

        let (c_V, lambda) = sample_soil_layers(&soil_layers, 8., 2).unwrap();
        assert_eq!(c_V, vec![6.75, 4.]);
        assert_eq!(lambda, vec![0., 0.]);

        let soil_layers = [SoilLayerProperties {
            d: std::f64::INFINITY,
            rho: 1.,
            c: 2.,
            lambda: 3.,
        }];
        let (c_V, lambda) = sample_soil_layers(&soil_layers, 6., 2).unwrap();
        assert_eq!(c_V, vec![2., 2.]);
        assert_eq!(lambda, vec![3., 3.]);
    }
}
