# Mathematical Foundations Reference

Applied mathematics reference for the AI Principal Engineer skill.
Read this file when proofs, derivations, numerical methods, or optimization theory are needed.

---

## 1. Linear Algebra for ML

### Essential Operations

| Operation | Notation | ML Use Case | Complexity |
|-----------|----------|-------------|------------|
| Matrix multiply | C = AB | Forward pass, attention | O(n*m*k) |
| SVD | A = UΣV^T | Dimensionality reduction, LoRA | O(min(mn^2, m^2n)) |
| Eigendecomposition | Av = λv | PCA, spectral clustering, Hessian analysis | O(n^3) |
| QR factorization | A = QR | Least squares, orthogonalization | O(mn^2) |
| Cholesky | A = LL^T | Gaussian processes, covariance inversion | O(n^3/3) |
| Kronecker product | A ⊗ B | Factored attention, parameter-efficient layers | O(n^2*m^2) |

### Tensor Operations

**Einstein summation** (the universal tool for tensor contractions):

```python
import numpy as np

# Batch matrix multiply: (B, M, K) x (B, K, N) -> (B, M, N)
C = np.einsum("bmk,bkn->bmn", A, B)

# Attention scores: (B, H, S, D) x (B, H, S, D) -> (B, H, S, S)
scores = np.einsum("bhsd,bhtd->bhst", Q, K) / np.sqrt(d_k)

# Trace of batch matrices: (B, N, N) -> (B,)
traces = np.einsum("bii->b", matrices)

# Outer product: (M,) x (N,) -> (M, N)
outer = np.einsum("i,j->ij", u, v)
```

### Low-Rank Approximations

**LoRA** (Low-Rank Adaptation) mathematical basis:

```
W_new = W_frozen + BA

where:
  W_frozen ∈ R^{d×k}   (frozen pretrained weights)
  B ∈ R^{d×r}           (trainable, r << min(d,k))
  A ∈ R^{r×k}           (trainable)
  r = rank (typically 4-64)
```

Parameter savings: from d*k to r*(d+k). For d=k=4096, r=16: 99.2% reduction.

**Truncated SVD** for initialization:

```python
U, S, Vt = np.linalg.svd(W, full_matrices=False)
A = np.diag(np.sqrt(S[:r])) @ Vt[:r, :]
B = U[:, :r] @ np.diag(np.sqrt(S[:r]))
# W ≈ B @ A
```

---

## 2. Calculus & Optimization

### Gradient Computation

**Chain rule in computational graphs** (backpropagation):

```
Loss = f(g(h(x, W1), W2), W3)

∂Loss/∂W1 = (∂f/∂g) · (∂g/∂h) · (∂h/∂W1)
```

Each node stores its local Jacobian; backward pass multiplies them in reverse order.

**Jacobian vs Hessian**:

| Matrix | Size | Contains | Use |
|--------|------|----------|-----|
| Jacobian J | m × n | ∂f_i/∂x_j | First-order sensitivity |
| Hessian H | n × n | ∂²f/∂x_i∂x_j | Curvature, Newton's method |

Hessian is O(n^2) storage — for large models, use Hessian-vector products (O(n) via `torch.autograd.functional.hvp`).

### Optimization Algorithms

**Adam / AdamW** (default for transformers):

```
m_t = β1 * m_{t-1} + (1 - β1) * g_t          # first moment (mean)
v_t = β2 * v_{t-1} + (1 - β2) * g_t^2        # second moment (variance)
m̂_t = m_t / (1 - β1^t)                        # bias correction
v̂_t = v_t / (1 - β2^t)                        # bias correction

Adam:   θ_t = θ_{t-1} - lr * m̂_t / (√v̂_t + ε)
AdamW:  θ_t = θ_{t-1} - lr * (m̂_t / (√v̂_t + ε) + λ * θ_{t-1})
```

AdamW decouples weight decay from the adaptive learning rate — critical for transformer training.

**Learning rate schedules**:

| Schedule | Formula | When |
|----------|---------|------|
| Cosine annealing | lr * 0.5 * (1 + cos(π * t/T)) | Standard transformer pretraining |
| Linear warmup | lr * t/warmup_steps | First 1-10% of training |
| Cosine with warm restarts | Cosine with periodic resets | Long training, escaping local minima |
| Inverse sqrt | lr * sqrt(warmup) / sqrt(t) | Original transformer schedule |

**Practical defaults** (transformer fine-tuning):

```python
lr = 2e-5            # base learning rate
warmup_ratio = 0.06  # 6% of total steps
weight_decay = 0.01  # AdamW
beta1 = 0.9
beta2 = 0.999
eps = 1e-8
max_grad_norm = 1.0  # gradient clipping
```

### Numerical Stability

**Log-sum-exp trick** (prevents overflow in softmax):

```python
def stable_softmax(logits):
    max_logit = logits.max(dim=-1, keepdim=True).values
    exp_logits = torch.exp(logits - max_logit)
    return exp_logits / exp_logits.sum(dim=-1, keepdim=True)
```

**Mixed-precision loss scaling**:

```python
scaler = torch.amp.GradScaler()

with torch.autocast(device_type="cuda", dtype=torch.float16):
    loss = model(inputs)

scaler.scale(loss).backward()
scaler.unscale_(optimizer)
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
scaler.step(optimizer)
scaler.update()
```

---

## 3. Probability & Statistics

### Distributions in ML

| Distribution | Use Case | Key Property |
|-------------|----------|-------------|
| Gaussian (Normal) | Weight init, noise injection, VAE latents | Closed-form KL divergence |
| Categorical | Token prediction, classification | Softmax output layer |
| Bernoulli | Dropout, binary classification | p(x=1) = σ(z) |
| Dirichlet | Topic models, mixture weights | Conjugate prior for Categorical |
| Gumbel-Softmax | Differentiable discrete sampling | Reparameterization trick for categoricals |

### Information Theory

| Quantity | Formula | ML Application |
|----------|---------|----------------|
| Entropy | H(X) = -Σ p(x) log p(x) | Uncertainty in predictions |
| Cross-entropy | H(p,q) = -Σ p(x) log q(x) | Classification loss |
| KL divergence | D_KL(p\|\|q) = Σ p(x) log(p(x)/q(x)) | VAE regularization, knowledge distillation |
| Mutual information | I(X;Y) = H(X) - H(X\|Y) | Feature selection, representation learning |

**Cross-entropy loss** (the workhorse of classification):

```python
loss = F.cross_entropy(logits, targets)
# Equivalent to: F.nll_loss(F.log_softmax(logits, dim=-1), targets)
# Numerically stable: combines log_softmax + nll_loss internally
```

### Attention Mechanism Mathematics

**Scaled dot-product attention**:

```
Attention(Q, K, V) = softmax(QK^T / √d_k) V

where:
  Q ∈ R^{n×d_k}  (queries)
  K ∈ R^{m×d_k}  (keys)
  V ∈ R^{m×d_v}  (values)
  Output ∈ R^{n×d_v}

Scaling by 1/√d_k prevents softmax saturation for large d_k.
```

**Multi-head attention**:

```
MultiHead(Q, K, V) = Concat(head_1, ..., head_h) W^O

head_i = Attention(Q W_i^Q, K W_i^K, V W_i^V)

Parameters per head: 3 * d_model * d_k + d_v * d_model
Total: h * (3 * d_k + d_v) * d_model ≈ 4 * d_model^2  (when d_k = d_v = d_model/h)
```

**Flash Attention** complexity:

| Method | Time | Memory | Notes |
|--------|------|--------|-------|
| Standard | O(n^2 * d) | O(n^2) | Materializes full attention matrix |
| Flash Attention | O(n^2 * d) | O(n) | Tiled, fused kernel — same FLOPS, no n^2 memory |
| Flash Attention 2 | O(n^2 * d) | O(n) | Better parallelism, 2x faster than FA1 |

---

## 4. Convergence Theory

### Gradient Diagnostics

| Symptom | Diagnosis | Fix |
|---------|-----------|-----|
| Loss = NaN after few steps | Gradient explosion | Reduce lr, add gradient clipping, check data |
| Loss plateaus early | Vanishing gradients or saddle point | Residual connections, LayerNorm, lr warmup |
| Train loss drops, val loss rises | Overfitting | Dropout, weight decay, early stopping, more data |
| Loss oscillates | lr too high | Reduce lr, use scheduler with warmup |
| Loss decreases very slowly | lr too low or poor initialization | Increase lr, use Kaiming/Xavier init |

### Weight Initialization

| Method | Formula | When |
|--------|---------|------|
| Xavier (Glorot) | W ~ U(-√(6/(n_in+n_out)), √(6/(n_in+n_out))) | Sigmoid/tanh activations |
| Kaiming (He) | W ~ N(0, √(2/n_in)) | ReLU/GELU activations |
| Zero | bias = 0 | Bias terms, residual branch outputs |
| Normal (0.02) | W ~ N(0, 0.02) | Transformer (GPT-style) convention |

### Batch Size Scaling

**Linear scaling rule**: When multiplying batch size by k, multiply learning rate by k (up to a limit).

```
Effective batch size = micro_batch * gradient_accumulation_steps * num_gpus
If base_lr was tuned at batch_size=32, and you scale to 256:
  new_lr = base_lr * (256/32) = base_lr * 8

Use warmup to stabilize: warmup_steps = base_warmup * (256/32)
```

This breaks down above batch_size ~8K for most models — use LARS/LAMB optimizers for very large batches.

---

## 5. Regularization Theory

| Method | Math | Effect |
|--------|------|--------|
| L1 (Lasso) | λ Σ\|w_i\| | Sparsity (drives weights to exactly 0) |
| L2 (Ridge / Weight Decay) | λ Σ w_i^2 | Shrinkage (prefers small weights) |
| Dropout | Randomly zero p fraction of activations | Implicit ensemble, prevents co-adaptation |
| Label smoothing | target = (1-ε)*one_hot + ε/K | Prevents overconfident predictions |
| Spectral normalization | W / σ(W) where σ = largest singular value | Lipschitz constraint, stabilizes GANs |
| Gradient penalty | λ \|\|∇_x D(x)\|\|^2 | WGAN-GP stability |
