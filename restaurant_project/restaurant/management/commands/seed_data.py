from django.core.management.base import BaseCommand
from restaurant.models import FoodItem
MENU=[
("🍛","Biryani","Main Course","Fragrant rice, tender meat and aromatic spices.",180,"https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=700&q=85"),
("🍚","Fried Rice","Main Course","Wok-fried rice with vegetables and savory seasoning.",140,"https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=700&q=85"),
("🥟","Dumplings","Snacks","Steamed dumplings served with a spicy dip.",120,"https://images.unsplash.com/photo-1496116218417-1a781b1c416c?w=700&q=85"),
("🌮","Taco","Fast Food","Crispy taco loaded with fresh fillings.",90,"https://images.unsplash.com/photo-1552332386-f8dd00dc2f85?w=700&q=85"),
("🌯","Burrito","Fast Food","Soft tortilla packed with flavorful fillings.",130,"https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=700&q=85"),
("🍤","Shrimp","Main Course","Crispy golden shrimp with house sauce.",170,"https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?w=700&q=85"),
("🐟","Fish Fry","Main Course","Crispy fried fish with lemon and herbs.",160,"https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=700&q=85"),
("🥩","Steak","Main Course","Juicy grilled steak with signature seasoning.",250,"https://images.unsplash.com/photo-1546964124-0cce460f38ef?w=700&q=85"),
("🍔","Cheese Burger","Fast Food","Beef patty, cheese, lettuce and house sauce.",120,"https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=700&q=85"),
("🍗","Fried Chicken","Fast Food","Crispy seasoned chicken pieces.",160,"https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=700&q=85"),
("🍕","Chicken Pizza","Fast Food","Cheesy pizza topped with seasoned chicken.",220,"https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=700&q=85"),
("🍝","Chicken Pasta","Main Course","Creamy pasta with tender chicken.",180,"https://images.unsplash.com/photo-1555949258-eb67b1ef0ceb?w=700&q=85"),
("🍟","French Fries","Snacks","Crispy golden fries with seasoning.",80,"https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=700&q=85"),
("🥗","Fresh Salad","Snacks","Fresh mixed salad with light dressing.",80,"https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=700&q=85"),
("🍫","Brownie","Dessert","Rich chocolate brownie.",85,"https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=700&q=85"),
("🍰","Chocolate Cake","Dessert","Moist chocolate cake with creamy frosting.",110,"https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=700&q=85"),
("🍨","Ice Cream","Dessert","Creamy vanilla ice cream.",70,"https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=700&q=85"),
("🥤","Soft Drink","Drinks","Chilled carbonated soft drink.",40,"https://images.unsplash.com/photo-1544145945-f90425340c7e?w=700&q=85"),
("☕","Coffee","Drinks","Freshly brewed hot coffee.",60,"https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=700&q=85"),
("🥭","Mango Juice","Drinks","Fresh mango juice.",90,"https://images.unsplash.com/photo-1623065422902-30a2d299bbe4?w=700&q=85"),
("🍋","Lemonade","Drinks","Fresh sweet and tangy lemonade.",60,"https://images.unsplash.com/photo-1523677011781-c91d1bbe2f3b?w=700&q=85"),
("🍗","Chicken Wings","Fast Food","Crispy spicy chicken wings with house dip.",150,"https://images.unsplash.com/photo-1527477396000-e27163b481c2?w=700&q=85"),
("🍔","Chicken Burger","Fast Food","Grilled chicken burger with fresh lettuce and sauce.",130,"https://images.unsplash.com/photo-1606755962773-d324e0a13086?w=700&q=85"),
("🌭","Hot Dog","Fast Food","Juicy sausage in a soft toasted bun.",100,"https://images.unsplash.com/photo-1612392062631-94dd858cba88?w=700&q=85"),
("🍕","Margherita Pizza","Fast Food","Classic pizza with tomato, mozzarella and basil.",190,"https://images.unsplash.com/photo-1579751626657-72bc17010498?w=700&q=85"),
("🍝","Creamy Alfredo Pasta","Main Course","Creamy pasta tossed with parmesan and herbs.",190,"https://images.unsplash.com/photo-1473093295043-cdd812d0e601?w=700&q=85"),
("🍛","Chicken Curry","Main Course","Tender chicken cooked in a rich aromatic curry.",200,"https://images.unsplash.com/photo-1601050690597-df0568f70950?w=700&q=85"),
("🍲","Thai Soup","Main Course","Hot and flavorful Thai-style soup with vegetables.",140,"https://images.unsplash.com/photo-1547592166-23ac45744acd?w=700&q=85"),
("🥪","Club Sandwich","Snacks","Triple-layer sandwich with chicken, egg and fresh vegetables.",150,"https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=700&q=85"),
("🧀","Cheese Nachos","Snacks","Crunchy nachos topped with melted cheese and salsa.",120,"https://images.unsplash.com/photo-1513456852971-30c0b8199d4d?w=700&q=85"),
("🍩","Donut","Dessert","Soft glazed donut with a sweet finish.",65,"https://images.unsplash.com/photo-1551024601-bec78aea704b?w=700&q=85"),
("🍮","Caramel Pudding","Dessert","Silky caramel pudding with a smooth texture.",75,"https://images.unsplash.com/photo-1488477181946-6428a0291777?w=700&q=85"),
("🍓","Strawberry Cake","Dessert","Light sponge cake with strawberry cream.",120,"https://images.unsplash.com/photo-1464349095431-e9a21285b5f3?w=700&q=85"),
("🧋","Milk Tea","Drinks","Creamy chilled milk tea served with ice.",80,"https://images.unsplash.com/photo-1558857563-b371033873b8?w=700&q=85"),
("🍊","Orange Juice","Drinks","Freshly squeezed orange juice.",90,"https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=700&q=85"),
]
class Command(BaseCommand):
    help="Seed FoodieHub with sample food items."
    def handle(self,*args,**options):
        for i,(emoji,name,cat,desc,price,url) in enumerate(MENU):
            obj,_=FoodItem.objects.get_or_create(name=name,defaults={"emoji":emoji,"category":cat,"description":desc,"price":price,"image_url":url,"available":True,"featured":i<8})
            obj.emoji=emoji; obj.category=cat; obj.description=desc; obj.price=price; obj.image_url=url; obj.available=True; obj.featured=i<8; obj.save()
        self.stdout.write(self.style.SUCCESS(f"Seed complete. {len(MENU)} food items added/updated."))
