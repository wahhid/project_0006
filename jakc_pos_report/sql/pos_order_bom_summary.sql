SELECT  
  product_bom_line.name_template,
  sum(mrp_bom_line.product_qty * pos_order_line.qty) as total_qty
FROM pos_order
LEFT JOIN pos_order_line ON pos_order.id = pos_order_line.order_id 
LEFT JOIN product_product ON pos_order_line.product_id = product_product.id
LEFT JOIN product_template on product_template.id = product_product.product_tmpl_id
LEFT JOIN mrp_bom ON product_template.id = mrp_bom.product_tmpl_id
LEFT JOIN mrp_bom_line ON mrp_bom.id = mrp_bom_line.bom_id
LEFT JOIN product_product as product_bom_line ON mrp_bom_line.product_id = product_bom_line.id
WHERE 
  pos_order_line.product_id IN (125)
GROUP BY
  product_bom_line.name_template