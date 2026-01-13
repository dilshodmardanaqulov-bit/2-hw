from django.shortcuts import render, redirect
from .models import Enemy, Item
import random


def home(request):
    """Home page with game introduction and start button"""
    return render(request, 'game/home.html')


def start_game(request):
    """Initialize a new game session"""
    # Clear any existing game data
    request.session.flush()
    
    # Initialize game state
    request.session['player_health'] = 100
    request.session['player_max_health'] = 100
    request.session['inventory'] = []
    request.session['current_enemy'] = None
    request.session['location'] = 'forest'
    request.session['enemies_defeated'] = 0
    request.session['game_over'] = False
    request.session['victory'] = False
    
    return redirect('play')


def play(request):
    """Main game interface"""
    # Get game state from session
    player_health = request.session.get('player_health', 100)
    player_max_health = request.session.get('player_max_health', 100)
    inventory = request.session.get('inventory', [])
    current_enemy = request.session.get('current_enemy')
    location = request.session.get('location', 'forest')
    enemies_defeated = request.session.get('enemies_defeated', 0)
    
    # Check game over conditions
    if player_health <= 0:
        request.session['game_over'] = True
        return redirect('game_over')
    
    if enemies_defeated >= 10:
        request.session['victory'] = True
        return redirect('victory')
    
    # Spawn random enemy if none exists
    if not current_enemy:
        enemies = list(Enemy.objects.all())
        if enemies:
            enemy = random.choice(enemies)
            request.session['current_enemy'] = {
                'name': enemy.name,
                'health': enemy.health,
                'max_health': enemy.health,
                'attack_power': enemy.attack_power,
                'description': enemy.description
            }
            current_enemy = request.session['current_enemy']
    
    # Get and clear message
    message = request.session.pop('message', None)
    
    # Check if player has potions for heal button
    has_potion = any(item['type'] == 'potion' for item in inventory)
    
    context = {
        'player_health': player_health,
        'player_max_health': player_max_health,
        'inventory': inventory,
        'current_enemy': current_enemy,
        'location': location,
        'enemies_defeated': enemies_defeated,
        'message': message,
        'has_potion': has_potion,
    }
    
    return render(request, 'game/play.html', context)


def move(request):
    """Handle player movement to new locations"""
    if request.session.get('game_over') or request.session.get('victory'):
        return redirect('play')
    
    locations = ['forest', 'cave', 'mountain', 'village']
    current_location = request.session.get('location', 'forest')
    
    # Move to a different location
    new_location = random.choice([loc for loc in locations if loc != current_location])
    request.session['location'] = new_location
    
    # 30% chance to find an item
    if random.random() < 0.3:
        items = list(Item.objects.all())
        if items:
            item = random.choice(items)
            inventory = request.session.get('inventory', [])
            inventory.append({
                'name': item.name,
                'type': item.item_type,
                'effect_value': item.effect_value,
                'description': item.description
            })
            request.session['inventory'] = inventory
            request.session['message'] = f"You moved to the {new_location} and found a {item.name}!"
        else:
            request.session['message'] = f"You moved to the {new_location}."
    else:
        request.session['message'] = f"You moved to the {new_location}."
    
    # Clear current enemy when moving
    request.session['current_enemy'] = None
    
    return redirect('play')


def attack(request):
    """Handle combat with current enemy"""
    if request.session.get('game_over') or request.session.get('victory'):
        return redirect('play')
    
    current_enemy = request.session.get('current_enemy')
    if not current_enemy:
        request.session['message'] = "No enemy to attack!"
        return redirect('play')
    
    # Player attacks enemy
    player_damage = random.randint(8, 15)
    current_enemy['health'] -= player_damage
    
    # Check if enemy is defeated
    if current_enemy['health'] <= 0:
        enemies_defeated = request.session.get('enemies_defeated', 0)
        request.session['enemies_defeated'] = enemies_defeated + 1
        request.session['current_enemy'] = None
        
        # 50% chance to find treasure
        if random.random() < 0.5:
            items = list(Item.objects.filter(item_type='treasure'))
            if items:
                item = random.choice(items)
                inventory = request.session.get('inventory', [])
                inventory.append({
                    'name': item.name,
                    'type': item.item_type,
                    'effect_value': item.effect_value,
                    'description': item.description
                })
                request.session['inventory'] = inventory
                request.session['message'] = f"You defeated the {current_enemy['name']}! You found a {item.name}!"
            else:
                request.session['message'] = f"You defeated the {current_enemy['name']}!"
        else:
            request.session['message'] = f"You defeated the {current_enemy['name']}!"
    else:
        # Enemy attacks back
        enemy_damage = current_enemy['attack_power'] + random.randint(-2, 2)
        player_health = request.session.get('player_health', 100)
        player_health = max(0, player_health - enemy_damage)
        request.session['player_health'] = player_health
        request.session['current_enemy'] = current_enemy
        request.session['message'] = f"You attacked the {current_enemy['name']} for {player_damage} damage! The {current_enemy['name']} attacked you for {enemy_damage} damage!"
    
    return redirect('play')


def heal(request):
    """Handle healing using potions"""
    if request.session.get('game_over') or request.session.get('victory'):
        return redirect('play')
    
    inventory = request.session.get('inventory', [])
    player_health = request.session.get('player_health', 100)
    player_max_health = request.session.get('player_max_health', 100)
    
    # Find first potion in inventory
    potion_index = None
    for i, item in enumerate(inventory):
        if item['type'] == 'potion':
            potion_index = i
            break
    
    if potion_index is not None:
        potion = inventory[potion_index]
        heal_amount = potion['effect_value']
        player_health = min(player_max_health, player_health + heal_amount)
        request.session['player_health'] = player_health
        
        # Remove used potion
        inventory.pop(potion_index)
        request.session['inventory'] = inventory
        request.session['message'] = f"You used a {potion['name']} and restored {heal_amount} health!"
    else:
        request.session['message'] = "You don't have any potions to heal!"
    
    return redirect('play')


def game_over(request):
    """Game over page"""
    enemies_defeated = request.session.get('enemies_defeated', 0)
    context = {
        'enemies_defeated': enemies_defeated,
    }
    return render(request, 'game/game_over.html', context)


def victory(request):
    """Victory page"""
    enemies_defeated = request.session.get('enemies_defeated', 0)
    context = {
        'enemies_defeated': enemies_defeated,
    }
    return render(request, 'game/victory.html', context)
