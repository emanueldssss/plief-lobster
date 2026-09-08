# Validação — Pli'ef Lobster v2

Implementado a partir do ZIP fornecido, versão 2.0.0. Commit local `f45380f`. O pacote contém 20 arquivos e mantém LICENSE/NOTICE byte a byte. Não houve instalação global nem modificação das skills instaladas.

## Execuções

- `python -m unittest discover -s tests -v`: 48 casos descobertos, 47 passaram e 1 foi pulado no pacote isolado por depender dos pacotes separados Sifr/Orun.
- O mesmo caso de integração foi executado separadamente contra os motores reais encontrados na instalação local, com a raiz de resolução ajustada somente no processo de teste: passou. Total: 48 casos executados com sucesso entre as duas configurações.
- `quick_validate.py work/plief-lobster`: `Skill is valid!`.
- CLI exercitada por subprocesso: research cria rascunho e recusa sobrescrita; research-verify, craft-check e verify aceitam fixtures completas; rascunho incompleto e entradas ausentes retornam os códigos documentados.
- Verificados casos negativos de hashes alterados, arquivos ausentes, caminhos absolutos/traversal, URL com credenciais fictícias, registros malformados, pesquisa dispensada indevidamente, falta de impacto, fonte apenas referencial usada como aquisição, nota central <=2 e screenshot usado sozinho como evidência temporal.
- Links internos: válidos. Sete referências a arquivos de companions externos continuam declaradas; esses pacotes não fazem parte deste ZIP.
- Evals: IDs L-01 a L-20 presentes e estrutura válida. Os oito novos cenários foram adicionados; não foram executados como sessões completas de agentes criando interfaces.
- `git diff --staged --check`: passou. Inspeção de código/documentos e varredura de marcadores de segredo/pendência sem achados. Não há novas dependências Python.
- ZIP: CRC e comparação byte a byte de todos os arquivos passaram.

## Cobertura dos critérios do pedido

Esta matriz verifica implementação do contrato, não eficácia estética em produção.

| Critério | Implementação |
| --- | --- |
| Pesquisa obrigatória em trabalho expressivo substancial | SKILL, research-contract; receipt v2 rejeita dispensa |
| Resultados retidos como evidência | sources.evidence com hash; candidates e implementation_impacts |
| Busca além dos índices Orun | reference-fabric, descoberta dinâmica pelo host |
| Open Props | Catálogo prioritário de tokens/motion/type/material |
| VibePrompt | Referência visual/padrões; aquisição condicional separada |
| ReUI | Fonte prioritária de aquisição, API inspecionada antes do uso |
| DesignSystems.one | Inteligência de design systems, sem falsa aquisição |
| 21st.dev | Descoberta de componentes de primeira classe |
| Registries shadcn | Diretório oficial e busca por item |
| Aceternity/Magic UI/React Bits | Fontes expressivas explícitas |
| Primitivos headless | Prioridade estrutural e comportamental |
| Contrato 3D | 3d-craft e gate próprio |
| Modelo/material/textura/render separados | Critérios 3D e seis dimensões adicionais |
| Contrato de animação | motion-craft e motion_evidence |
| Contrato de scroll | scroll-craft, comportamento e matriz de entrada/restauração |
| Contrato de tipografia | typography-craft, aquisição e render |
| Blur/material | material-craft com critérios explícitos |
| Amnésia de componentes proibida | Destino e impacto obrigatórios; aquisição ligada ao componente externo |
| Substituto custom justificado | Regra preservada e teste v1/v2 |
| Referências afetam implementação | Impactos vinculados ao owner e a provas atuais |
| Performance/fallback para efeitos pesados | performance_budget e evidências de check |
| Screenshots inspecionados por craft | craft-review e gate visual independente |
| Evidência temporal | motion_evidence exige interação observada |
| Evidência 3D | 3d_evidence exige dados de cena e provas visual/interação |
| Correção e craft separados no receipt | Cinco craft_gates; v1 explicitamente legado |

## Limitações e avaliação

O CLI valida registros, referências e integridade de arquivos. Não comprova que uma observação é verdadeira, que a licença foi interpretada corretamente, que as fontes são diversas na prática ou que o render é bom. O perfil e as dimensões centrais precisam ser conferidos contra o pedido; hashes não descobrem dependências omitidas pelo autor do receipt.

As fontes prioritárias foram consultadas nas páginas [Open Props](https://open-props.style), [VibePrompt](https://vibeprompts.dev), [ReUI](https://reui.io), [DesignSystems.one](https://www.designsystems.one/design-systems), [shadcn registries](https://ui.shadcn.com/docs/directory) e [21st.dev](https://21st.dev). ReUI não retornou corpo legível pela ferramenta de texto; o catálogo deixa explícita a necessidade de inspecionar sua API durante aquisição. O catálogo completo contém sementes de pesquisa, não uma certificação atual de todos os provedores.

Segurança: validação dos novos caminhos, hashes, tipos e URLs foi exercitada. Não foram encontrados problemas de severidade alta na revisão. Autenticidade e qualidade continuam sob inspeção do resultado real.

Nota da entrega: **B**. Implementação e integridade verificadas; eficácia em um ciclo completo de frontend com render ainda não verificada.

SHA-256 do ZIP: `044c56a127d27544cc20aa4cdaa5a4044d644332a3c605616166c91597451cc5`.
