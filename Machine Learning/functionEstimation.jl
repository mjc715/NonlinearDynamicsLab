using DataDrivenDiffEq, ModelingToolkit, OrdinaryDiffEq
using DataDrivenSparse, LinearAlgebra, StableRNGs, Plots

rng = StableRNG(1000)

function f(u, p, t)  # Make function depend on t as well
    x = 2.0 * u[1] * t
    return [x]
end

u0 = [1.0]
tspan = (0.0, 3.0)
dt = 0.1
prob = ODEProblem(f, u0, tspan)
sol = solve(prob, Tsit5(), saveat=dt)

X = sol[:, :] + 0.2 .* randn(rng, size(sol)) # Making random data
ts = sol.t

prob = ContinuousDataDrivenProblem(X, ts, GaussianKernel(),) # What does this part specify?

@variables u[1:1]
u = collect(u)

# h = Num[polynomial_basis(u, 5)]
basis = Basis(polynomial_basis(u, 5), u)

sampler = DataProcessing(split=0.8, shuffle=true, batchsize=25, rng=rng)
lambdas = exp10.(-10:0.1:0)
opt = STLSQ(lambdas) # How does the optimization work?
res = solve(prob, basis, opt, options=DataDrivenCommonOptions(data_processing=sampler, digits=1))
system = get_basis(res)
params = get_parameter_map(system)
println(system)
println(params)
display(plot(plot(prob), plot(res), layout=(1, 2)))
sleep(10)



# Find function without random dataset:
# 
# ddprob = DataDrivenProblem(sol)
# @variables t x(t)
# u = [x]
# basis = Basis(polynomial_basis(u, 5), u, iv=t)
# opt = STLSQ(exp10.(-5:0.1:-1))
# ddsol = solve(ddprob, basis, opt, options=DataDrivenCommonOptions(digits=1))
# println(get_basis(ddsol))