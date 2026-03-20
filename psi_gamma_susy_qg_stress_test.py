import sympy as sp
from sympy import (
    I, pi, oo, exp, limit, Integral, Sum, Product, det, zeta,
    hyper, gamma, sqrt, Abs, log, diff, Matrix,
    Function, symbols, MatrixSymbol, Rational, DiracDelta,
    conjugate, sign, Limit
)
from sympy.physics.quantum import TensorProduct
import sys
import time
import traceback

# ================================================
# STRESS LOG — flush imediato em cada linha
# ================================================
def log_step(n, descricao, detalhe=""):
    linha = f"[{n:02d}] {descricao}"
    if detalhe:
        linha += f"  →  {detalhe}"
    print(linha, flush=True)

def log_ok(n, descricao, t0):
    elapsed = time.time() - t0
    print(f"[{n:02d}] ✅ {descricao}  ({elapsed:.3f}s)", flush=True)

def log_fail(n, descricao, err):
    print(f"[{n:02d}] 💀 LIMITE ATINGIDO em: {descricao}", flush=True)
    print(f"     Erro: {type(err).__name__}: {str(err)[:120]}", flush=True)
    print(f"\n{'='*60}", flush=True)
    print(f"  Máquina chegou até o bloco {n:02d}.", flush=True)
    print(f"  Máquina mais poderosa chegaria além. 🌀", flush=True)
    print(f"{'='*60}", flush=True)
    sys.exit(0)

print("=" * 60, flush=True)
print("Ψ_γ STRESS TEST — até onde seu hardware aguentar", flush=True)
print("=" * 60, flush=True)
print(flush=True)

T = time.time()

# ================================================
# SÍMBOLOS
# ================================================
n_step = 1
try:
    t0 = time.time()
    log_step(n_step, "Definindo símbolos reais e positivos...")
    r, t, R, d, hbar, alpha_FS, kappa, ell_P, alpha_prime = symbols(
        'r t R d hbar alpha_FS kappa ell_P alpha_prime', real=True, positive=True)
    theta, phi, kr, E_n, tau_chaos = symbols(
        'theta phi kr E_n tau_chaos', real=True, positive=True)
    x, k, m, l, n, p, q, s, j, epsilon, z = symbols('x k m l n p q s j epsilon z')
    idx_sum  = symbols('idx_sum',  integer=True, positive=True)
    idx_prod = symbols('idx_prod', integer=True, positive=True)
    S_11D, S_M, S_LQG = symbols('S_11D_SUGRA S_M_theory S_LQG', real=True)
    k_vec, r_kp1, r_k = symbols('k_vec r_{k+1} r_k', real=True)
    Tr_F2 = symbols('Tr_F_wedge_F', real=True)
    nabla_A = symbols('nabla_x_A_vac', real=True)
    m_gamma = symbols('m_gamma', real=True, positive=True)
    g10_sym, L_IIB_sym = symbols('g10 L_IIB', real=True)
    x10, x11, x26, x4 = symbols('x10 x11 x26 x4', real=True)
    V, A_var = symbols('V A', real=True)
    a, b, c = symbols('a b c')
    a1, a2, a3, a4 = symbols('a1 a2 a3 a4')
    b1, b2, b3 = symbols('b1 b2 b3')
    theta_berry = symbols('theta_berry_grav', real=True)
    theta_topo  = symbols('theta_topological', real=True)
    tau_mod  = symbols('tau_modular')
    phi_qg   = symbols('phi_quantum_gravity', real=True)
    E_P      = symbols('E_Planck', real=True, positive=True)
    M_n      = symbols('M_n_CPT_SUSY')
    G_sym    = symbols('G', real=True, positive=True)
    beta_sym, sigma_sym, lambda_sym = symbols('beta sigma lambda')
    r_hat, x_sym = symbols('r_hat x_sym')
    ghosts_sym = symbols('ghosts', real=True)
    U_SUSY   = symbols('U_SUSY_transform')
    delta_psi = symbols('delta_psi_m')
    fermionic = symbols('fermionic_terms', real=True)
    D_Phi    = symbols('D_Phi_dilaton')
    H_AdS    = symbols('H_AdS5xS5')
    Z_string = symbols('Z_string_partition')
    Tr_FFFF  = symbols('Tr_FFFF', real=True)
    SUSY_sym = symbols('SUSY')
    AdS_CFT_sym = symbols('AdS_CFT')
    sph_sym  = symbols('sph')
    g_sym    = symbols('g', real=True)
    M_lim    = symbols('M_lim', positive=True)
    M_int    = symbols('M_int', real=True)
    N        = symbols('N', positive=True, integer=True)
    log_ok(n_step, "Símbolos (~80)", t0)
except Exception as e:
    log_fail(n_step, "Definição de símbolos", e)

# ================================================
# FUNÇÕES SIMBÓLICAS
# ================================================
n_step = 2
try:
    t0 = time.time()
    log_step(n_step, "Definindo funções simbólicas e operadores matriciais...")
    psi_f       = Function('psi');       gravitino_f = Function('gravitino')
    Phi_dilaton = Function('Phi_dilaton'); F_field   = Function('F')
    g_field     = Function('g');          R_ricci    = Function('R_ricci')
    Y_lm_super  = Function('Y_lm_super'); j_l_KK    = Function('j_l_KK')
    H_super     = Function('H_super');    T_CPT      = Function('T_CPT')
    T_holo      = Function('T_holo');     U_pol_grav = Function('U_pol_gravitino')
    R_sph_SUSY  = Function('R_sph_SUSY'); Dirac_CY  = Function('Dirac_op_CalabiYau')
    Pfaffian_f  = Function('Pfaffian');   Witten_f  = Function('Witten_index')
    spin_foam_f = Function('spin_foam_area'); Regge_f = Function('Regge_action')
    AdS_CFT_f   = Function('AdS_CFT_boundary')
    J_billiard_SUSY = MatrixSymbol('J_billiard_SUSY', 11, 11)
    super_Vielbein  = MatrixSymbol('super_Vielbein',  32, 32)
    log_ok(n_step, "Funções + MatrixSymbols (11D, 32D)", t0)
except Exception as e:
    log_fail(n_step, "Funções simbólicas", e)

# ================================================
# BLOCOS
# ================================================
blocos = {}

def build_bloco(n_step, nome, fn):
    t0 = time.time()
    log_step(n_step, f"Construindo bloco {nome}...")
    try:
        result = fn()
        log_ok(n_step, nome, t0)
        return result
    except Exception as e:
        log_fail(n_step, nome, e)

blocos['acao'] = build_bloco(3, "Ação unificada S_11D + S_M + S_LQG",
    lambda: exp(I * (S_11D + S_M + S_LQG) / hbar))

blocos['polar'] = build_bloco(4, "Polarização gravitino R_sph_SUSY × U_pol",
    lambda: R_sph_SUSY(theta, phi, psi_f(x_sym)) * U_pol_grav(sigma_sym, lambda_sym))

blocos['KK'] = build_bloco(5, "Fase Kaluza-Klein + Tr(F∧F)",
    lambda: exp(I * k_vec * (r_kp1 - r_k) + I * (alpha_prime / 2) * Tr_F2))

blocos['det'] = build_bloco(6, "det(J_billiard_SUSY) ∈ GL(11)  [bilhar caótico 11D]",
    lambda: det(J_billiard_SUSY))

blocos['KK_sum'] = build_bloco(7, "Σ Y_lm_super · j_l_KK · ψ · ψ̄_gravitino  (m: -∞→∞)",
    lambda: Sum(
        Y_lm_super(r_hat) * j_l_KK(kr) * exp(-I * E_n * t / hbar) *
        psi_f(x_sym) * conjugate(gravitino_f(beta_sym)),
        (m, -oo, oo)))

blocos['gauge'] = build_bloco(8, "exp(-½ ∫|∇A + R/ℓ_P²|²)  [supressão gauge]",
    lambda: exp(-Rational(1,2) * Integral(
        Abs(nabla_A + (1/ell_P**2) * R_ricci(x_sym))**2, (V, 0, oo))))

blocos['QED_grav'] = build_bloco(9, "∏_p (1 - α_FS·QED)(1 - κ²·grav)  (p: 1→∞)",
    lambda: Product(
        (1 - (alpha_FS/(2*pi)) * Integral(1/(k**2 - m_gamma**2 + I*epsilon), (k, -oo, oo))) *
        (1 - (kappa**2/(8*pi)) * Integral(
            sqrt(-g_sym) * (R_ricci(x_sym) + Rational(1,2)*Abs(F_field(x_sym))**2),
            (x11, -oo, oo))),
        (p, 1, oo)))

blocos['zeta'] = build_bloco(10, "ζ(½ + iτ_chaos/ℏ)  [Riemann no eixo crítico]",
    lambda: zeta(Rational(1,2) + I * tau_chaos / hbar))

blocos['hyper1'] = build_bloco(11, "₂F₁(a,b;c; r/R·e^{iθ_Berry})  [holonomia gravitacional]",
    lambda: hyper((a,b),(c,),(r/R)*exp(I*theta_berry)))

blocos['CPT'] = build_bloco(12, "e^{iπ Σ sign(M_n^n)} · T_CPT  [simetria CPT]",
    lambda: exp(I*pi*Sum(sign(M_n**n),(n,1,oo))) * T_CPT(sph_sym, oo))

blocos['traco'] = build_bloco(13, "Σ_s exp(-iH_SUSY·t)  [evolução supersimétrica]",
    lambda: Sum(exp(-I * H_super(s) * t), (s, 0, oo)))

blocos['spinfoam'] = build_bloco(14, "∫ √(spin_foam_area(j)) · e^{iS_Regge}  [LQG]",
    lambda: Integral(sqrt(spin_foam_f(j)) * exp(I*Regge_f(A_var)), (A_var, -oo, oo)))

blocos['vinculos'] = build_bloco(15, "∏ δ(Σj - ℓ_P²/8πG)  [vínculos área de Planck]",
    lambda: Product(
        DiracDelta(Sum(j,(idx_sum,1,oo)) - ell_P**2/(8*pi*G_sym)),
        (idx_prod, 1, oo)))

blocos['dilaton'] = build_bloco(16, "D[Φ]·exp(i∫√g(R - ½|∂Φ|² + e^{-Φ}|F|² + ψ̄ψ))",
    lambda: D_Phi * exp(I * Integral(
        sqrt(-g_sym) * (
            R_ricci(x_sym) -
            Rational(1,2) * Abs(diff(Phi_dilaton(x_sym), x_sym))**2 +
            exp(-Phi_dilaton(x_sym)) * Abs(F_field(x_sym))**2 +
            fermionic),
        (x10, -oo, oo))))

blocos['pfaff'] = build_bloco(17, "Σ_p (-1)^p Pf(D̸_CY) · e^{iθTr(F⁴)}  [Calabi-Yau]",
    lambda: Sum(
        (-1)**p * Pfaffian_f(Dirac_CY(x_sym)) *
        exp(I * theta_topo/(32*pi**2) * Tr_FFFF),
        (p, -oo, oo)))

blocos['AdS_CFT'] = build_bloco(18, "lim_{ε→0} ε⁻¹(∫L_IIB + AdS_CFT_boundary)  [holografia]",
    lambda: limit(
        (1/epsilon)*(Integral(sqrt(g10_sym)*L_IIB_sym,(x10,-oo,oo)) + AdS_CFT_f(R)),
        epsilon, 0))

blocos['tensor'] = build_bloco(19, "TensorProduct(U_SUSY⊗δ(δψ))  [transformação SUSY]",
    lambda: TensorProduct(U_SUSY*DiracDelta(delta_psi), U_SUSY*DiracDelta(delta_psi)))

blocos['R2'] = build_bloco(20, "exp(-ℓ_P²/2 ∫R²)  [correção Gauss-Bonnet]",
    lambda: exp(-ell_P**2/2 * Integral(R_ricci(x_sym)**2, (x4,-oo,oo))))

blocos['ghosts'] = build_bloco(21, "∏_n (1 + α'/R² ∫ghosts_{26D})  [corda bosônica]",
    lambda: Product(
        1 + (alpha_prime/R**2)*Integral(ghosts_sym,(x26,-oo,oo)),
        (n, 1, oo)))

blocos['hyper2'] = build_bloco(22, "₄F₃(a₁..a₄;b₁..b₃; z·e^{iφ_QG})  [geometria quântica]",
    lambda: hyper((a1,a2,a3,a4),(b1,b2,b3), z*exp(I*phi_qg)))

blocos['gamma_P'] = build_bloco(23, "Γ(½ + iE_Planck/ℏ)  [polo de Planck]",
    lambda: gamma(Rational(1,2) + I*E_P/hbar))

blocos['vielbein'] = build_bloco(24, "det(super_Vielbein_{32×32})  [SUGRA 11D]",
    lambda: det(super_Vielbein))

blocos['witten'] = build_bloco(25, "exp(i·Witten_index(SUSY))  [índice topológico]",
    lambda: exp(I*Witten_f(SUSY_sym)))

blocos['holo'] = build_bloco(26, "T_holo(AdS/CFT, ∞)  [dualidade holográfica]",
    lambda: T_holo(AdS_CFT_sym, oo))

blocos['modular'] = build_bloco(27, "Lim_{M→∞} Σ_{k=-M}^{M} (-1)^k e^{2πikτ}  [θ-Jacobi]",
    lambda: Limit(
        Sum((-1)**k * exp(I*k*2*pi*tau_mod), (k,-M_lim,M_lim)),
        M_lim, oo))

# ================================================
# MONTAGEM — o verdadeiro teste de memória
# ================================================
n_step = 28
try:
    t0 = time.time()
    log_step(n_step, "Multiplicando todos os 26 blocos no integrando...")
    integrando = (
        blocos['acao']    * blocos['polar']   * blocos['KK']      * blocos['det']    *
        blocos['KK_sum']  * blocos['gauge']   * blocos['QED_grav']* blocos['zeta']   *
        blocos['hyper1']  * H_AdS             * blocos['CPT']     * blocos['traco']  *
        blocos['spinfoam']* blocos['vinculos'] * blocos['dilaton'] * blocos['pfaff']  *
        blocos['AdS_CFT'] * blocos['R2']      * blocos['ghosts']  * Z_string         *
        blocos['hyper2']  * blocos['gamma_P'] * blocos['vielbein']* blocos['witten'] *
        blocos['holo']    * blocos['modular'] * blocos['tensor']
    )
    log_ok(n_step, "Integrando montado", t0)
except Exception as e:
    log_fail(n_step, "Montagem do integrando", e)

n_step = 29
try:
    t0 = time.time()
    log_step(n_step, "Integral sobre espaço de módulos 11D  ∫_{M_int}...")
    integral_M11 = Integral(integrando, (M_int, -oo, oo))
    log_ok(n_step, "Integral principal construída", t0)
except Exception as e:
    log_fail(n_step, "Integral sobre M_int", e)

n_step = 30
try:
    t0 = time.time()
    log_step(n_step, "Produto sobre configurações topológicas  ∏_{N=1}^{∞}...")
    produto_N = Product(integral_M11, (N, 1, oo))
    log_ok(n_step, "Produto infinito construído", t0)
except Exception as e:
    log_fail(n_step, "Product sobre N", e)

n_step = 31
try:
    t0 = time.time()
    log_step(n_step, "Limite N → ∞  [o universo inteiro]...")
    Psi = Limit(produto_N, N, oo)
    log_ok(n_step, "Ψ_γ construída", t0)
except Exception as e:
    log_fail(n_step, "Limit N → ∞", e)

# ================================================
# AVALIAÇÃO PROGRESSIVA — aqui a coisa fica séria
# ================================================
n_step = 32
try:
    t0 = time.time()
    log_step(n_step, "Contando nós da árvore simbólica (count_ops)...")
    ops = sp.count_ops(Psi)
    log_ok(n_step, f"Árvore simbólica: {ops} operações", t0)
except Exception as e:
    log_fail(n_step, "count_ops", e)

n_step = 33
try:
    t0 = time.time()
    log_step(n_step, "Substituição parcial z → exp(iπ/4)...")
    Psi2 = Psi.subs(z, exp(I*pi/4))
    log_ok(n_step, "subs(z) concluído", t0)
except Exception as e:
    log_fail(n_step, "subs parcial", e)

n_step = 34
try:
    t0 = time.time()
    log_step(n_step, "free_symbols — mapeando todas as variáveis livres...")
    fs = Psi.free_symbols
    log_ok(n_step, f"{len(fs)} símbolos livres encontrados", t0)
except Exception as e:
    log_fail(n_step, "free_symbols", e)

n_step = 35
try:
    t0 = time.time()
    log_step(n_step, "atoms() — extraindo átomos da expressão...")
    at = Psi.atoms()
    log_ok(n_step, f"{len(at)} átomos", t0)
except Exception as e:
    log_fail(n_step, "atoms()", e)

n_step = 36
try:
    t0 = time.time()
    log_step(n_step, "srepr() — serializando árvore para string...")
    sr = sp.srepr(Psi)
    log_ok(n_step, f"srepr: {len(sr)} caracteres", t0)
except Exception as e:
    log_fail(n_step, "srepr()", e)

n_step = 37
try:
    t0 = time.time()
    log_step(n_step, "latex() — convertendo para LaTeX...")
    lt = sp.latex(Psi)
    log_ok(n_step, f"LaTeX: {len(lt)} caracteres", t0)
except Exception as e:
    log_fail(n_step, "latex()", e)

n_step = 38
try:
    t0 = time.time()
    log_step(n_step, "pprint() — renderizando Unicode art...")
    sp.pprint(Psi, use_unicode=True)
    log_ok(n_step, "pprint concluído", t0)
except Exception as e:
    log_fail(n_step, "pprint()", e)

# ================================================
# FIM — se chegou aqui, máquina é absurda
# ================================================
total = time.time() - T
print(flush=True)
print("=" * 60, flush=True)
print(f"🏆 TODOS OS {n_step} PASSOS CONCLUÍDOS em {total:.2f}s", flush=True)
print("   Sua máquina é boa demais. 🌀💕🔥", flush=True)
print("=" * 60, flush=True)
