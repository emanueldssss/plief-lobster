# Lobster 2.1 — Platform Capability Scout

Incluído references/platform-capability-scout.md e integrado ao pipeline, catálogo, motion, scroll e receipt. O Scout compara recursos nativos, soluções híbridas e bibliotecas por subfeature, navegadores-alvo, custo, acessibilidade e fallback observado. verify --require-platform exige o registro; um Scout anexado é validado mesmo sem a flag. Receipts anteriores permanecem legíveis sem a exigência adicional.

Verificação executada: python -m unittest discover -s tests -q, 55 casos descobertos: 54 passaram no pacote isolado e 1 integração Sifr/Orun foi pulada por ausência dos siblings naquele diretório. Esse caso foi executado separadamente contra os motores reais da instalação e passou. Os sete testes novos cobrem escolhas native/hybrid/library, omissão, validação automática de anexos, falso fallback temporal, hashes alterados, campos malformados e CLI. quick_validate.py: Skill is valid. Links internos, oito novas referências desde v1, 24 casos de eval, atribuição original e diff check conferidos.

Na revisão, o texto português de L-12 apresentou corrupção por decodificação implícita do Windows. Uma asserção reproduziu a divergência; a leitura UTF-8 e restauração dos primeiros 12 casos a partir do ZIP original passaram na comparação dos valores JSON. A conferência foi adicionada ao validador de entrega.

Fontes oficiais consultadas: [web.dev janeiro/2026](https://web.dev/blog/web-platform-01-2026?hl=en), [Baseline](https://web.dev/baseline), [MDN View Transitions](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API), [animation-timeline](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/animation-timeline), [anchor-name](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/anchor-name). Anchor Positioning entrou como Baseline Newly available em janeiro/2026; o contrato exige verificar cada subfeature e o público real, sem tratar Baseline como cobertura universal.

Limites: não houve instalação global nem execução dos evals como sessões completas de construção visual. O CLI verifica integridade e suficiência estrutural dos registros; a verdade das observações e o comportamento de APIs em cada navegador dependem de execução real. A extensão implementa o Scout, mas não encerra a validação visual completa pendente da Lobster. Não atribuo nota S a essa evidência. Avaliação: implementação do Scout verificada; eficácia visual integral ainda não verificada.

Segurança: caminhos e hashes usam o verificador existente; entradas inválidas são rejeitadas, sem novas dependências nem execução de URLs. Nenhum achado alto conhecido. Atualização de suporte e veracidade dos registros permanecem responsabilidades explícitas da inspeção.

Commit local: 8674e47. ZIP: 22 arquivos, CRC e comparação byte a byte passaram. SHA-256: 4d28c586b2ae038d156ebc6116101d73d84d0eabace3cd175c23e73b106b6d5d.
