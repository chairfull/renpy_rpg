---
type: zone
id: downtown
name: Downtown Los Angeles
desc: Camarilla-controlled financial district and political center.
subtype: city
---

# Apartment Complex

## Your Apartment
```yaml
type: zone
subtype: room
objects:
  front_door:
    type: [link, area]
    position: [300, 0, 0]
    link_zone: downtown#apartment_hall
    link_area: your_apartment_door
  window:
    type: [link, area]
    link_zone: santa_monica#street
    link_area: your_window
```

## Apartment Hall
```yaml
type: zone
```