SELECT 
  pos_order.id, 
  pos_order_line.name,
  pos_order_line.product_id, 
  pos_order_line.qty as pos_order_line_qty,
  mrp_bom.id as mrp_bom_id,
  product_bom_line.name_template,
  mrp_bom_line.product_qty as mrp_bom_line_product_qty,
  mrp_bom_line.product_qty * pos_order_line.qty as total_qty
FROM pos_order
LEFT JOIN pos_order_line ON pos_order.id = pos_order_line.order_id 
LEFT JOIN product_product ON pos_order_line.product_id = product_product.id
LEFT JOIN product_template on product_template.id = product_product.product_tmpl_id
LEFT JOIN mrp_bom ON product_template.id = mrp_bom.product_tmpl_id
LEFT JOIN mrp_bom_line ON mrp_bom.id = mrp_bom_line.bom_id
LEFT JOIN product_product as product_bom_line ON mrp_bom_line.product_id = product_bom_line.id
WHERE 
  pos_order_line.product_id = 125
ORDER BY id;