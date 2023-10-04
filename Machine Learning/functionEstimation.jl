using DataDrivenDiffEq, ModelingToolkit, OrdinaryDiffEq
using DataDrivenSparse, LinearAlgebra, StableRNGs, Plots

rng = StableRNG(1000)

# Ctrl-Shift-P -> Start REPL -> pwd() -> cd("Machine Learning") -> include("____")
# Define own variable using ModelingToolkit and have it be equal to a function. Use this in basis

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
@variables u[1:2] x y t
@parameters p
u = collect(u)

basis1 = x * y
basis2 = 1
basis3 = [basis1, basis2]
# h = Num[u; F]
# basis = Basis(h, F)
# basis = Basis([u, F(t)], u)

sampler = DataProcessing(split=0.8, shuffle=true, batchsize=25, rng=rng)
lambdas = exp10.(-10:0.1:0)
opt = STLSQ(lambdas, 1.0)
res = solve(prob, basis3, opt, options=DataDrivenCommonOptions(data_processing=sampler, digits=2))

system = get_basis(res)
params = get_parameter_map(system)

# Displaying results
println(system)
println(params)
display(plot(plot(prob), plot(res), layout=(1, 2)))