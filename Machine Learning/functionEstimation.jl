using DataDrivenDiffEq, ModelingToolkit, OrdinaryDiffEq
using DataDrivenSparse, LinearAlgebra, StableRNGs, Plots

rng = StableRNG(1000)

# Ctrl-Shift-P -> Start REPL -> pwd() -> cd("Machine Learning") -> include("____")
# Work on preventing overfitting

function f(u, p, t)
    x, y = u
    dx = 2.0 * x * y
    dy = 1
    return [dx, dy]
end

# Setting initial conditions
u0 = [1.0; 0]
tspan = (0.0, 2.0)
dt = 0.0001

# Solving ODE Problem
prob = ODEProblem(f, u0, tspan)
sol = solve(prob, Tsit5(), saveat=dt)

# Adding noise to solution 
X = sol[:, :] + 0.2 .* randn(rng, size(sol))
ts = sol.t

prob = ContinuousDataDrivenProblem(X, ts, GaussianKernel(),)

@variables u[1:2]
u = collect(u)

h = Num[polynomial_basis(u, 2); u]
basis = Basis(h, u)

sampler = DataProcessing(split=0.8, shuffle=true, batchsize=25, rng=rng)
lambdas = exp10.(-10:0.1:0)
opt = STLSQ(lambdas)
res = solve(prob, basis, opt, options=DataDrivenCommonOptions(data_processing=sampler, digits=2))

system = get_basis(res)
params = get_parameter_map(system)

# Displaying results
println(system)
println(params)
display(plot(plot(prob), plot(res), layout=(1, 2)))
