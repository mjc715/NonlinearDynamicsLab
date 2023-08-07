using DataDrivenDiffEq, ModelingToolkit, OrdinaryDiffEq
using DataDrivenSparse, LinearAlgebra

function f(u, p, t)
    x = 2.0 * u[1]
    return [x]
end

u0 = [1.0]
tspan = (0.0, 10.0)
dt = 0.1
prob = ODEProblem(f, u0, tspan)
sol = solve(prob, Tsit5(), saveat=dt)

ddprob = DataDrivenProblem(sol)

@variables t x(t)
u = [x]
basis = Basis(polynomial_basis(u, 5), u, iv=t)  # Not working
opt = STLSQ(exp10.(-5:0.1:-1))
ddsol = solve(ddprob, basis, opt, options=DataDrivenCommonOptions(digits=1))
println(get_basis(ddsol))
