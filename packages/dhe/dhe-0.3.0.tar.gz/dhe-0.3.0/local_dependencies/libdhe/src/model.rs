/// Material properties
#[derive(Clone, Debug)]
pub struct MaterialProperties {
    /// Density [kg/m^3]
    pub rho: f64,
    /// Specific heat [J/kg/K]
    pub c: f64,
    /// Heat conductivity [W/m/K]
    pub lambda: f64,
}

/// Backfill properties
pub type FillProperties = MaterialProperties;

impl Default for FillProperties {
    fn default() -> Self {
        Self {
            rho: 1180.,
            c: 3040.,
            lambda: 0.81,
        }
    }
}

/// Fluid properties
#[derive(Clone, Debug)]
pub struct FluidProperties {
    /// Density [kg/m^3]
    pub rho: f64,
    /// Specific heat [J/kg/K]
    pub c: f64,
    /// Heat conductivity [W/m/K]
    pub lambda: f64,
    /// Kinematic viscosity of brine [m^2/s]
    pub nu: f64,
}

/// Brine properties
///
/// Specific heat:
///   H2O: 4200 J/kg/K
///   33 % Etylen glycol: 3800 J/kg/K
/// Kinematic viscosity:
///   H2O: 0.00000175 m^2/s
///   33 % Ethylene glycol: ~ 0.000006 m^2/s
pub type BrineProperties = FluidProperties;

impl Default for BrineProperties {
    fn default() -> Self {
        Self {
            rho: 1050.,
            c: 3875.,
            lambda: 0.449,
            nu: 0.415E-5,
        }
    }
}

/// Soil layer properties
#[derive(Clone, Debug)]
pub struct SoilLayerProperties {
    /// Density [kg/m^3]
    pub rho: f64,
    /// Specific heat [J/kg/K]
    pub c: f64,
    /// Heat conductivity [W/m/K]
    pub lambda: f64,
    /// Thickness of layer [m]
    pub d: f64,
}

impl Default for SoilLayerProperties {
    fn default() -> Self {
        Self {
            rho: 2600.,
            c: 1000.,
            lambda: 2.,
            d: std::f64::INFINITY,
        }
    }
}

/// Parameters used to compute initial soil temperature
#[derive(Clone, Debug)]
pub struct SoilParameters {
    /// Mean temperature of soil [°C]
    pub T_soil_mean: f64,
    /// Axial gradient of temperature of soil [K/m]
    pub T_grad: f64,
}
impl Default for SoilParameters {
    fn default() -> Self {
        Self {
            T_soil_mean: 9.8,
            T_grad: 0.03,
        }
    }
}

#[derive(Clone, Debug)]
pub struct TSoil0Parameters {
    /// Values of g function at ln(t/ts) = (-4, -2, 0, 2, 3)
    pub g_coefs: [f64; 5],
    /// Distance of DHE [m]
    pub d_DHE: f64,
}
impl Default for TSoil0Parameters {
    fn default() -> Self {
        Self {
            g_coefs: [4.82, 5.69, 6.29, 6.57, 6.60],
            d_DHE: 10.,
        }
    }
}

/// Boundary condition according to cone formula by Werner
#[derive(Clone, Debug)]
pub struct GConeParameters;

/// Downhole heat exchanger
#[derive(Clone, Debug)]
pub struct DHE {
    /// x coordinate of the DHE [m]
    pub x: f64,
    /// y coordinate of the DHE [m]
    pub y: f64,
    /// Length of DHE [m]
    pub L: f64,
    /// Diameter of DHE [m]
    pub D: f64,
    /// Diameter of bore hole [m]
    pub D_borehole: f64,
    /// Thickness of DHE pipe [m]
    pub thickness: f64,
    /// Thermal pipe resistance [Km/W]
    pub Ra: f64,
    /// Borehole thermal resistance [Km/W]
    pub Rb: f64,
    /// Thermal resistance [Km/W]
    pub R1: f64,
    pub fill_properties: FillProperties,
    pub brine_properties: BrineProperties,
    /// Mass throughput per DHE if pump is on [kg/s]
    pub Phi_m: f64,
    pub T_soil_0_parameters: TSoil0Parameters,
}

impl Default for DHE {
    fn default() -> Self {
        DHE {
            x: 0.0,
            y: 0.0,
            L: 100.0,
            D: 0.026,
            D_borehole: 0.115,
            thickness: 0.0,
            Ra: 0.0,
            Rb: 0.1,
            R1: 0.0,
            fill_properties: FillProperties::default(),
            T_soil_0_parameters: TSoil0Parameters::default(),
            brine_properties: BrineProperties::default(),
            Phi_m: 0.4,
        }
    }
}

#[derive(Clone, Debug)]
pub struct GlobalParameters {
    /// Number of sampling points in axial direction
    pub dim_ax: usize,
    /// Number of sampling points in radial direction
    pub dim_rad: usize,

    /// Soil layers
    pub soil_layers: Vec<SoilLayerProperties>,

    /// Radius of calculation [m]
    pub R: f64,
    /// Multiplier for the n_steps variable
    pub optimal_n_steps_multiplier: f64,
    /// Grid parameter for radial partition of domain of calculation
    pub Gamma: f64,
    /// Fraction of adiabatic boundary contitions
    pub adiabat: f64,
    /// Factor for n_steps [m]
    pub n_steps_0: usize,
    /// Duration between two boundary condition refreshes [s]
    pub dt_boundary_refresh: f64,
    /// Sampling step [s]
    pub dt: f64,
    /// [s]
    pub t0: f64,
    pub soil_parameters: SoilParameters,
}
impl Default for GlobalParameters {
    fn default() -> Self {
        Self {
            dim_ax: 4,
            dim_rad: 5,
            soil_layers: Vec::new(),
            R: 1.5,
            optimal_n_steps_multiplier: 2.0,
            Gamma: 2.0,
            adiabat: 0.0,
            n_steps_0: 4,
            dt_boundary_refresh: 7. * 24. * 3600.0,
            dt: 3600.0,
            t0: 0.0,
            soil_parameters: SoilParameters::default(),
        }
    }
}

#[derive(Clone, Debug)]
pub enum TBrineCalcMethod {
    Dynamic,
    Stationary,
}
impl Default for TBrineCalcMethod {
    fn default() -> Self {
        Self::Dynamic
    }
}

#[derive(Clone, Debug)]
pub enum CalculationMode {
    P(PCalculationMode),
}

/// Input: P
#[derive(Clone, Debug)]
pub struct PCalculationMode {
    /// Termination criterion for T_brine computation routine
    pub precision: f64,
}
impl Default for PCalculationMode {
    fn default() -> Self {
        Self { precision: 0.05 }
    }
}
