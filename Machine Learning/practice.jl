using DiffEqParamEstim, DifferentialEquations, Plots, Optimization, OptimizationOptimJL
using RecursiveArrayTools, ForwardDiff, OptimizationBBO, Optim

#--- Define the diff eq p = params
function f(u, p, t)
    du = p[1] * u
    return du
end

#--- Parameters for the DE
x_start = 1.0
p = [3.0]
tspan = (0.0, 10.0)
#--- Define problem and solve
prob = ODEProblem(f, x_start, tspan, p)
sol = solve(prob, Tsit5())
#--- Get times to test at
t = collect(range(0, stop=10, length=200))
#--- Getting noisy data points to reverse engineer params with
randomized = VectorOfArray([(sol(t[i]) .+ 0.01randn(1)) for i in 1:length(t)])
data = convert(Array, randomized)

# println(data)
# newprob = remake(prob, p=0.9)
# newsol = solve(newprob, Tsit5())
# plot(sol)
# display(plot!(newsol))
# sleep(10)

#--- What ML optimizes to get DE
cost_function = build_loss_objective(prob, Tsit5(), L2Loss(t, data),
    Optimization.AutoForwardDiff(),
    maxiters=10000, verbose=false)

# vals = 0.0:0.1:5.0
# display(plot(vals, [cost_function(i) for i in vals], yscale=:log10,
#     xaxis="Parameter", yaxis="Cost", title="1-Parameter Cost Function",
#     lw=3))
# sleep(10)

#--- Optimizing loss function and using result as parameter for DE
optprob = Optimization.OptimizationProblem(cost_function, [0.9])
optsol = solve(optprob, BFGS())
newprob = remake(prob, p=optsol.u)
newsol = solve(newprob, Tsit5())
plot(sol)
display(plot!(newsol))
println(optsol.u)
sleep(10)