using DataDrivenDiffEq, ModelingToolkit, OrdinaryDiffEq
using DataDrivenSparse, LinearAlgebra, StableRNGs, Plots

rng = StableRNG(1000)

# Ctrl-Shift-P -> Start REPL -> pwd() -> cd("Machine Learning") -> include("____")
# Look into ridge regression, complicate f_data, explain how code works

# f_data represents potential interpolating function
function f_data(x, y)
    return x + y
end

# Included time dependence by making dy = 1
function f(u, p, t)
    x, y = u
    dx = 2.0 * x * y + f_data(x, y)
    dy = 1
    return [dx, dy]
end

@register_symbolic f_data(x, y)

# Setting initial conditions
u0 = [1.0; 0]
tspan = (0.0, 2.0)
dt = 0.001

# Solving ODE Problem
prob = ODEProblem(f, u0, tspan)
sol = solve(prob, Tsit5(), saveat=dt)

# Adding noise to solution 
X = sol[:, :] + 0.2 .* randn(rng, size(sol))
ts = sol.t

prob = ContinuousDataDrivenProblem(X, ts, GaussianKernel(),)

@variables u[1:2] t
u = collect(u)
h = Num[polynomial_basis(u, 2); f_data(u[1:2]...)]
basis = Basis(h, u)


sampler = DataProcessing(split=0.8, shuffle=true, batchsize=25, rng=rng)
lambdas = exp10.(-10:0.1:0)
opt = STLSQ(lambdas, 1.0)
res = solve(prob, basis, opt, options=DataDrivenCommonOptions(data_processing=sampler, digits=2))

system = get_basis(res)
params = get_parameter_map(system)

# Displaying results
println(system)
println(params)
display(plot(plot(prob), plot(res), layout=(1, 2)))