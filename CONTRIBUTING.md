# Contribuindo

## Workflow

1. Crie uma branch `feature/` a partir de `develop`
2. Faça as alterações seguindo a [Constitution](.specify/memory/constitution.md)
3. Execute `make test` (cobertura ≥ 90%) e `make lint`
4. Abra um Pull Request para `develop`

## Padrões

- **CWE**: todo código deve mitigar CWE Top 25. Comentário: `# Prevents CWE-NNN`
- **Testes**: pytest + pytest-asyncio. fixtures em `tests/conftest.py`
- **Frontend**: data-testid em todos os elementos interativos
- **Commits**: [conventional commits](https://www.conventionalcommits.org/)

## Review

Toda PR deve verificar:
- [ ] CWE mitigations documentadas
- [ ] Testes passando com cobertura ≥ 90%
- [ ] data-testid presentes no frontend
- [ ] Licenciamento FOSS (sem dependências proprietárias)
