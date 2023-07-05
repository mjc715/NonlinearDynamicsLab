using Pkg
Pkg.add("DiffEqParamEstim")
Pkg.add("DifferentialEquations")
Pkg.add("Plots")
Pkg.add("RecursiveArrayTools")
using DiffEqParamEstim, DifferentialEquations, Plots

f(x, p, t) = p * x
x_start = 10.0
p = 1.0
tspan = (0.0, 1.0)
prob = ODEProblem(f, x_start, tspan, p)
sol = solve(prob)

#??????????????????????????????????????????????????

using RecursiveArrayTools # for VectorOfArray
t = collect(range(0, stop=10, length=200))
function generate_data(t)
    sol = solve(prob)
    randomized = VectorOfArray([(sol(t[i]) + 0.01randn(2)) for i in 1:length(t)])
    data = convert(Array, randomized)
end
aggregate_data = convert(Array, VectorOfArray([generate_data(t) for i in 1:10000]))
monte_prob = EnsembleProblem(prob)
obj = build_loss_objective(monte_prob, L2Loss(t, aggregate_data), Optimization.AutoForwardDiff(),
    maxiters=10000, verbose=false, trajectories=1000)
optprob = Optimization.OptimizationProblem(obj, [1.0, 0.5])
result = solve(optprob, Optim.BFGS())
println(result)
