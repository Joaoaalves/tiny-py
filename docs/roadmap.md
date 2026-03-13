# Roadmap

This page tracks what is already implemented and what is planned for future releases.

---

## Currently implemented (v0.1.0)

| Resource | Method | Endpoint |
|----------|--------|----------|
| **Products** | `search` / `iter_search` | `produto.pesquisa.php` |
| **Products** | `get` | `produto.obter.php` |
| **Products** | `get_stock` | `produto.obter.estoque.php` |
| **Products** | `update_stock` | `produto.atualizar.estoque.php` |
| **Products** | `update_price` | `produto.atualizar.preco.php` |
| **Orders** | `search` / `iter_search` | `pedido.pesquisa.php` |
| **Orders** | `get` | `pedido.obter.php` |

---

## v0.2.0 — Account & Contacts

Foundation resources needed by most integrations.

### Dados da Conta

| Method | Endpoint | Description |
|--------|----------|-------------|
| `account.info()` | `info.php` | Fetch account details (plan, CNPJ, name) |

### Clientes e Fornecedores (`ContactsResource`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `contacts.search(…)` / `iter_search(…)` | `contato.pesquisa.php` | Search contacts with filters |
| `contacts.get(contact_id)` | `contato.obter.php` | Fetch a single contact |
| `contacts.create(request)` | `contato.incluir.php` | Create a new contact |
| `contacts.update(contact_id, request)` | `contato.alterar.php` | Update an existing contact |

### Products — missing operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `products.create(request)` | `produto.incluir.php` | Create a new product |
| `products.update(product_id, request)` | `produto.alterar.php` | Update an existing product |
| `products.get_structure(product_id)` | `produto.obter.estrutura.php` | Fetch product BOM / kit structure |
| `products.get_tags(product_id)` | `produto.obter.tags.php` | Fetch tags attached to a product |
| `products.list_updated(…)` | `produto.obter.atualizados.php` | List products changed since a given date |
| `products.list_stock_updates(…)` | `produto.obter.atualizacoes.estoque.php` | List stock change events |
| `products.get_category_tree()` | `produto.obter.arvore.categorias.php` | Fetch full category hierarchy |

---

## v0.3.0 — Tags, Price Lists & Sellers

### Grupos de Tags de Produtos (`ProductTagGroupsResource`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `product_tag_groups.search(…)` | `produto.grupos.tags.pesquisa.php` | Search tag groups |
| `product_tag_groups.create(request)` | `produto.grupos.tags.incluir.php` | Create a tag group |
| `product_tag_groups.update(group_id, request)` | `produto.grupos.tags.alterar.php` | Update a tag group |

### Tags de Produtos (`ProductTagsResource`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `product_tags.search(…)` | `produto.tags.pesquisa.php` | Search tags |
| `product_tags.create(request)` | `produto.tags.incluir.php` | Create a tag |
| `product_tags.update(tag_id, request)` | `produto.tags.alterar.php` | Update a tag |

### Listas de Preços (`PriceListsResource`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `price_lists.search(…)` | `lista.precos.pesquisa.php` | Search price lists |
| `price_lists.get_exceptions(list_id)` | `lista.precos.excecoes.php` | Fetch per-product price overrides |

### Vendedores (`SellersResource`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `sellers.search(…)` | `vendedor.pesquisa.php` | List sellers |

---

## v0.4.0 — Financial

### Contas a Receber (`ReceivablesResource`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `receivables.search(…)` / `iter_search(…)` | `conta.receber.pesquisa.php` | Search receivable accounts |
| `receivables.get(account_id)` | `conta.receber.obter.php` | Fetch a receivable |
| `receivables.create(request)` | `conta.receber.incluir.php` | Create a receivable |
| `receivables.update(account_id, request)` | `conta.receber.alterar.php` | Update a receivable |
| `receivables.settle(account_id, request)` | `conta.receber.baixar.php` | Mark as settled |
| `receivables.get_payment_methods()` | `formas.recebimento.pesquisa.php` | List accepted payment methods |

### Contas a Pagar (`PayablesResource`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `payables.search(…)` / `iter_search(…)` | `conta.pagar.pesquisa.php` | Search payable accounts |
| `payables.get(account_id)` | `conta.pagar.obter.php` | Fetch a payable |
| `payables.create(request)` | `conta.pagar.incluir.php` | Create a payable |
| `payables.settle(account_id, request)` | `conta.pagar.baixar.php` | Mark as settled |

### Fretes (`FreightResource`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `freight.quote(request)` | `frete.cotacao.php` | Get shipping quotes from carriers |

---

## v0.5.0 — Orders extended operations

Extends the existing `OrdersResource` with write and lifecycle methods.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `orders.create(request)` | `pedido.incluir.php` | Create a new order |
| `orders.update(order_id, request)` | `pedido.alterar.php` | Update an order |
| `orders.generate_production_order(order_id)` | `pedido.gerar.ordemproducao.php` | Generate a production order |
| `orders.generate_invoice(order_id)` | `pedido.gerar.nota.fiscal.php` | Generate fiscal note from order |
| `orders.update_shipping(order_id, request)` | `pedido.atualizar.informacoes.despacho.php` | Update dispatch/tracking info |
| `orders.update_status(order_id, status)` | `pedido.atualizar.situacao.php` | Change order status |
| `orders.add_markers(order_id, markers)` | `pedido.incluir.marcadores.php` | Add markers/labels |
| `orders.remove_markers(order_id, markers)` | `pedido.remover.marcadores.php` | Remove markers/labels |
| `orders.post_stock(order_id)` | `pedido.lancar.estoque.php` | Commit stock movement for order |
| `orders.reverse_stock(order_id)` | `pedido.estornar.estoque.php` | Reverse stock movement |
| `orders.post_financials(order_id)` | `pedido.lancar.contas.php` | Generate receivable from order |
| `orders.reverse_financials(order_id)` | `pedido.estornar.contas.php` | Reverse financial entries |

---

## v0.6.0 — Fiscal Notes (NF-e)

New `InvoicesResource`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `invoices.search(…)` / `iter_search(…)` | `nota.fiscal.pesquisa.php` | Search fiscal notes |
| `invoices.get(invoice_id)` | `nota.fiscal.obter.php` | Fetch a note |
| `invoices.create(request)` | `nota.fiscal.incluir.php` | Create a fiscal note |
| `invoices.create_consumer(request)` | `nota.fiscal.incluir.consumidor.php` | Create NFC-e (consumer note) |
| `invoices.create_from_xml(xml)` | `nota.fiscal.incluir.xml.php` | Import from XML |
| `invoices.issue(invoice_id)` | `nota.fiscal.emitir.php` | Transmit to SEFAZ |
| `invoices.get_xml(invoice_id)` | `nota.fiscal.obter.xml.php` | Download signed XML |
| `invoices.get_link(invoice_id)` | `nota.fiscal.obter.link.php` | Get DANFE / share link |
| `invoices.add_markers(invoice_id, markers)` | `nota.fiscal.incluir.marcadores.php` | Add markers |
| `invoices.remove_markers(invoice_id, markers)` | `nota.fiscal.remover.marcadores.php` | Remove markers |
| `invoices.update_shipping(invoice_id, request)` | `nota.fiscal.atualizar.informacoes.despacho.php` | Update dispatch info |
| `invoices.post_stock(invoice_id)` | `nota.fiscal.lancar.estoque.php` | Commit stock movement |
| `invoices.post_financials(invoice_id)` | `nota.fiscal.lancar.contas.php` | Generate receivable |

### PDV (`PdvResource`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `pdv.get_order(order_id)` | `pdv.pedido.obter.php` | Fetch a PDV order |
| `pdv.search_orders(…)` | `pdv.pedido.pesquisa.php` | Search PDV orders |
| `pdv.search_products(…)` | `pdv.produto.pesquisa.php` | Search products in PDV context |
| `pdv.create_invoice_from_xml(xml)` | `pdv.nota.incluir.xml.php` | Import NF-e via XML |
| `pdv.cancel_invoice_from_xml(xml)` | `pdv.nota.cancelar.xml.php` | Cancel NF-e via XML |

---

## v0.7.0 — CRM

New `CrmResource`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `crm.list_stages()` | `crm.estagios.php` | List all CRM stages |
| `crm.search(…)` / `iter_search(…)` | `crm.pesquisa.php` | Search CRM subjects |
| `crm.get(subject_id)` | `crm.obter.php` | Fetch a subject |
| `crm.create(request)` | `crm.incluir.php` | Create a subject |
| `crm.add_action(subject_id, request)` | `crm.incluir.acao.php` | Add an action to a subject |
| `crm.update_stage(subject_id, stage)` | `crm.alterar.estagio.php` | Move subject to a new stage |
| `crm.update_action_status(action_id, status)` | `crm.alterar.situacao.acao.php` | Update action status |

---

## v0.8.0 — Expeditions & Shipping

New `ExpeditionsResource`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `expeditions.send_items(request)` | `expedicao.enviar.objetos.php` | Send items to an expedition |
| `expeditions.search(…)` / `iter_search(…)` | `expedicao.pesquisa.php` | Search expeditions |
| `expeditions.search_groups(…)` | `expedicao.agrupamentos.pesquisa.php` | Search groupings |
| `expeditions.get(expedition_id)` | `expedicao.obter.php` | Fetch expedition |
| `expeditions.update(expedition_id, request)` | `expedicao.alterar.php` | Update expedition |
| `expeditions.create_group(request)` | `expedicao.agrupamento.incluir.php` | Create a grouping |
| `expeditions.finish_group(group_id)` | `expedicao.agrupamento.concluir.php` | Finish a grouping |
| `expeditions.get_group_print(group_id)` | `expedicao.agrupamento.obter.impressao.php` | Get group print layout |
| `expeditions.get_labels(expedition_id)` | `expedicao.obter.etiquetas.php` | Download shipping labels |
| `expeditions.search_shipping_methods(…)` | `expedicao.formas.envio.pesquisa.php` | List available carriers |
| `expeditions.get_shipping_method(method_id)` | `expedicao.forma.envio.obter.php` | Fetch carrier details |
| `expeditions.create_shipping_method(request)` | `expedicao.forma.envio.incluir.php` | Create a shipping method |
| `expeditions.create_freight_method(request)` | `expedicao.forma.frete.incluir.php` | Create a freight method |

---

## v0.9.0 — NFS-e & Contracts & Separation

### Notas Fiscais de Serviço (`ServiceInvoicesResource`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `service_invoices.search(…)` / `iter_search(…)` | `nfse.pesquisa.php` | Search service notes |
| `service_invoices.get(invoice_id)` | `nfse.obter.php` | Fetch a service note |
| `service_invoices.create(request)` | `nfse.incluir.php` | Create a service note |
| `service_invoices.send(invoice_id)` | `nfse.enviar.php` | Transmit NFS-e |
| `service_invoices.query(invoice_id)` | `nfse.consultar.php` | Query transmission status |

### Contratos (`ContractsResource`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `contracts.search(…)` / `iter_search(…)` | `contrato.pesquisa.php` | Search contracts |
| `contracts.get(contract_id)` | `contrato.obter.php` | Fetch a contract |
| `contracts.create(request)` | `contrato.incluir.php` | Create a contract |
| `contracts.update(contract_id, request)` | `contrato.alterar.php` | Update a contract |
| `contracts.add_addon(contract_id, request)` | `contrato.adicional.incluir.php` | Add an addon to a contract |
| `contracts.search_addons(contract_id)` | `contrato.adicional.pesquisa.php` | List addons of a contract |
| `contracts.delete_addon(addon_id)` | `contrato.adicional.excluir.php` | Remove an addon |

### Separação (`SeparationResource`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `separation.search(…)` / `iter_search(…)` | `separacao.pesquisa.php` | Search separations |
| `separation.get(separation_id)` | `separacao.obter.php` | Fetch a separation |
| `separation.update_status(separation_id, status)` | `separacao.alterar.situacao.php` | Update separation status |

---

## Summary

| Version | Focus | Resources added |
|---------|-------|----------------|
| **v0.1.0** | Core | Products (read + stock/price), Orders (read) |
| **v0.2.0** | Foundation | Account info, Contacts, Products write + extended reads |
| **v0.3.0** | Catalogue | Product tags & groups, Price lists, Sellers |
| **v0.4.0** | Financial | Receivables, Payables, Freight quotes |
| **v0.5.0** | Orders extended | Full order lifecycle (write, stock, financials, status) |
| **v0.6.0** | Fiscal (NF-e) | Invoices full lifecycle, PDV |
| **v0.7.0** | CRM | Full CRM subject & action management |
| **v0.8.0** | Expeditions | Shipping, carriers, labels, groupings |
| **v0.9.0** | Services & ops | NFS-e, Contracts, Separation |
