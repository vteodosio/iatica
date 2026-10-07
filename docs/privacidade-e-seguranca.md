# Privacy & Access-Control Hardening (LGPD + Security)

> **Scope:** two feature areas — **A. privacy-by-design (LGPD)** and **B. access-control fixes** —
> plus one blocking bug found and fixed along the way (`SECRET_KEY` missing from `settings.py`).

---

## Summary

| Area | What changed | Why it matters |
|---|---|---|
| **A. Privacy (LGPD)** | Students join with a **nickname/alias** instead of their real name; username is now random; a **consent gate** is captured; teachers can **remove a student** (erasure). | The platform teaches kids not to share personal data — it must not collect real names itself. Aligns with LGPD (Brazil's GDPR). |
| **B. Access control** | Student routes now verify **group membership**; quiz results are **owner-only**. | Closed IDOR-style holes where a student could read other students' results or other groups' content via the URL. |
| **Bug fix** | Restored `SECRET_KEY` in `settings.py`. | Django cannot sign sessions/CSRF without it — the app was broken. |

**Verification:** 13 new tests pass · `manage.py check` clean · migration applied cleanly · all affected templates render.

---

## A. Privacy by design (LGPD)

### Problem (before)
`entrar_grupo` built the student's username from their **real name**:

```python
username = f"aluno_{codigo}_{nome_aluno.lower().replace(' ', '_')}"
```

…and stored the real first/last name. The platform's own lesson #4 tells kids *"never share personal info with AI"* while collecting their full names — a credibility and legal (LGPD) problem. It also meant two kids with the same name in the same group collided into one account.

### What changed

1. **Random, non-identifying username.** New `gerar_username_aluno()` returns `aluno_<16-hex>` (`secrets.token_hex`), never derived from the name.
2. **New `apelido` field** on `User` — the display name/nickname the child chooses. The entry form label changed from *"Seu Nome"* to *"Seu nome ou apelido"*.
3. **New `consentiu_em` field** — timestamp of when the privacy notice was accepted.
4. **Consent gate.** The student entry form now shows a short privacy notice and a required checkbox ("Li o aviso de privacidade e quero entrar."). Posting without consent is rejected and creates no user.
5. **`nome_exibicao()`** helper on `User` — returns the alias for students, full name for teachers. Used everywhere a name is displayed (group detail, report, PDF).
6. **"Remove student" action (LGPD erasure).** A 🗑️ button on the group detail page removes the membership, and **deletes the student `User` if it has no other memberships**.

### Returning-student behavior (unchanged UX)
Identity is still resolved by alias *within a group*: entering the same nickname in the same group reuses the same student (so progress is kept), without storing the real name.

### Files
| File | Change |
|---|---|
| `apps/accounts/models.py` | `apelido`, `consentiu_em`, `nome_exibicao()`, `gerar_username_aluno()`, `__str__` |
| `apps/accounts/migrations/0002_user_apelido_consentiu_em.py` | **new** — adds the two fields |
| `apps/accounts/admin.py` | exposes `apelido` / `consentiu_em` in the Django admin |
| `apps/groups/views.py` | `entrar_grupo` rewritten (alias + consent + random username) |
| `templates/groups/area_aluno.html` | consent checkbox + privacy notice + label change |
| `templates/groups/detalhe_grupo.html` | alias display + remove button |
| `templates/reports/relatorio_grupo.html` | alias display |
| `apps/reports/views.py` | PDF uses `nome_exibicao()` |

---

## B. Access-control fixes

### Problem (before)
Student pages trusted `session['aluno_id']` **without verifying group membership**, and quiz results had **no ownership check**:

1. **Quiz results were public-by-ID.** `resultado_quiz` did `get_object_or_404(TentativaQuiz, pk=tentativa_pk)` with no owner check — anyone could view any student's answers/score by guessing a sequential `tentativa_pk`.
2. **Cross-group access.** `sala_estudo`, `licao_detalhe`, `marcar_lida`, `iniciar_quiz`, `submeter_quiz` never confirmed the session student actually belongs to the group in the URL. A student in group A could open group B's lessons and quiz, and `iniciar_quiz` could create `TentativaQuiz` rows in arbitrary groups.

### What changed
A single, reusable helper in a new module:

- `apps/groups/access.py` → `get_aluno_membro(request, grupo_pk)` (returns `(aluno_id, grupo)` or `None`) and `require_aluno_membro(...)` (same, but redirects to the student area with a message on denial).

Applied to every student-facing view:

| View | Change |
|---|---|
| `sala_estudo` | membership required |
| `licao_detalhe` | membership required |
| `marcar_lida` (AJAX) | membership required (returns `{ok: false}` if denied) |
| `iniciar_quiz` | membership required |
| `submeter_quiz` | membership required |
| `resultado_quiz` | **owner-only** — `tentativa.aluno_id == session aluno` or redirect |

### Files
| File | Change |
|---|---|
| `apps/groups/access.py` | **new** — membership helper |
| `apps/groups/views.py` | `sala_estudo` + `remover_aluno` use the helper |
| `apps/content/views.py` | `licao_detalhe` + `marcar_lida` membership |
| `apps/quiz/views.py` | `iniciar_quiz` / `submeter_quiz` membership; `resultado_quiz` ownership |
| `apps/groups/urls.py` | new `remover_aluno` route |

---

## Bug fix: `SECRET_KEY` restored

A recent commit (`cdb6d2c "removendo configurações desnecessarias"`) **removed `SECRET_KEY` from `settings.py`**. Django requires it to sign sessions/CSRF/messages — the app crashed on any authenticated or form-submitting request.

- `settings.py` → restored: `SECRET_KEY = config('SECRET_KEY', default='dev-secret-key-troque-em-producao')`
- The value still comes from `.env` (`SECRET_KEY=sua-chave-secreta-aqui-troque-em-producao`), which is git-ignored.

> ⚠️ **Note:** the `.env` value is a placeholder. For production, generate a strong, random key and set it via environment variable.

---

## Database migration

One new migration — **apply it before deploying**:

```bash
python manage.py migrate
# => Applying accounts.0002_user_apelido_consentiu_em... OK
```

It's backward-compatible: existing rows get `apelido=''` and `consentiu_em=NULL` (teachers keep using `first_name`/`last_name`).

---

## How to test

```bash
# run the test suite (13 tests)
python manage.py test apps.groups apps.quiz apps.content

# manual smoke test
python manage.py runserver
```

Manual checks:
1. **Student entry** (`/dashboard/alunos/`): enter a nickname + code → must tick the consent box → lands in the study room. Check the DB: username is `aluno_<hex>` (no name), `apelido` holds the nickname, `consentiu_em` is set.
2. **Returning student**: same nickname + same code → same user (no duplicate).
3. **Cross-group**: while in group A, manually hit group B's lesson/quiz URL → redirected to the student area.
4. **Result privacy**: open another student's `/quiz/resultado/<id>/` → redirected away.
5. **Remove student**: teacher clicks 🗑️ on a member → membership gone; student user deleted if it has no other groups.

---

## Behavior changes to review

- The consent checkbox is **required** to join (new form field). If your templates or scripts POST to `entrar_grupo` without `consentimento`, they'll now be rejected — update them.
- `submeter_quiz` now also requires the group to be **active** (previously it didn't check status). A finalized group no longer accepts submissions.
- Student names now come from the `apelido` field; any code that read `first_name`/`last_name` for students (there was none besides the entry flow) should switch to `nome_exibicao()`.

## Known limitations / follow-ups (out of scope here)

- **Alias collisions:** two *different* kids with the *same* nickname in the *same* group still share one account. A proper fix (per-group random secret token stored in the browser, or optional student accounts) is the "robust identity" work — tracked separately.
- **Full LGPD:** this adds data minimization + consent capture + erasure, but a complete compliance posture (lawful-basis with parents/guardians, DPIA, retention policy, DPO) is still needed before production.
- **Consent re-entry** doesn't refresh `consentiu_em` (kept as first-acceptance timestamp).

---

## Out of scope (other uncommitted changes in this working tree)

These are **not part of this PR** and were made earlier — commit them separately if desired:

- **Dark mode** — `templates/base.html`, `home.html`, `login.html`, `dashboard_professor.html`, `licao_detalhe.html`, `sala_estudo.html`, `quiz.html`, `resultado.html`.
- **`requirements.txt`** — `psycopg2-binary` bumped `2.9.9 → 2.9.13` (the pinned 2.9.9 has no Python 3.13 wheel).

Run `git status` to see the full list and stage only the files for this PR.
