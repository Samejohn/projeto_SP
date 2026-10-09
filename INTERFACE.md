# Interface do SPI

O visual usa os temas oficiais light (Solar), dark (Lunar), gourmet e soft do FlyonUI 2.4.1, com referência de organização visual no Vuexy. Os componentes existentes do AdminLTE/Bootstrap são preservados; o Vuexy comercial não foi incorporado. Soft usa a fonte Montserrat indicada na documentação, carregada pelo Google Fonts com alternativa local caso esteja indisponível.

O botão Tema aparece no cabeçalho e nas telas de acesso. A escolha é salva no navegador. Sem escolha salva, o sistema acompanha a preferência de claro/escuro do dispositivo.

## Compilar os estilos

Instale com `npm ci` e compile com `npm run build`. Os arquivos gerados em `static/css/flyonui.css` e `static/vendor/` estão incluídos para que o Django possa servi-los sem Node em produção. Execute `collectstatic` conforme a configuração de implantação.

Edite `static/src/theme.css` para configurar os temas e `static/css/interface.css` para ajustar a aparência. Novas classes Tailwind usam o prefixo `tw:` para evitar conflitos com os templates existentes. O seletor usa HTML nativo e não depende de plugins de dropdown.

Animate.css e Waves são servidos localmente. Movimento reduzido desativa animações e ondas. Referências: https://flyonui.com/docs/customization/themes/, https://animate.style/, https://flyonui.com/docs/third-party-plugins/wave-effect/.
