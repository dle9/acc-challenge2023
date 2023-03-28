from direct.showbase.ShowBase import ShowBase
from ursina import *
from ursina.shaders import lit_with_shadows_shader
from FirstPersonController import FirstPersonController
from Enemy import Enemy
from UI import UI



# ======================================================= WORLD ======================================================================
def skySetup():
    print("creating sky")
    sun = DirectionalLight()
    sun.look_at(Vec3(1, -1, -1))
    Sky()


def buildingSetup():
    print ("creating buildings")
    ground = Entity(model='plane', collider='box', scale=64)
    for i in range(16):
        Entity(model='cube', origin_y=-.5, scale=2, texture='brick', texture_scale=(1, 2),
            x=random.uniform(-20, 20),
            z=random.uniform(-8, 8) + 18,
            collider='box',
            scale_y=random.uniform(15, 25),
            color=color.hsv(0, 0, random.uniform(.9, 1))
            )


enemies = []

def enemySetup():
    global enemies
    print ("Spawning enemies")
    enemies = [Enemy(x=x * 10, target= player) for x in range(1)]
    mouse.traverse_target = Enemy.shootables_parent


def resetEnemies():
    global enemies
    print ("resetting enemies")
    for i in enemies:
        destroy(i)
    enemies = [Enemy(x=x * 8, target= player) for x in range(2)]


def worldSetup():
    random.seed(2023)
    Entity.default_shader = lit_with_shadows_shader

    skySetup()
    buildingSetup()
    enemySetup()
    print("World created")


app = Ursina()

# ======================================================= PLAYER/CAMERA ======================================================================
editor_camera = EditorCamera(enabled=False, ignore_paused=True)

player = FirstPersonController(model='cube', z=-10, color=color.orange, origin_y=-.5, speed=8)
player.collider = BoxCollider(player, Vec3(0, 1, 0), Vec3(1, 2, 1))

player.hp = 100
player.maxImmuneTimer = 0.8
player.immuneTimer = 0.8
healthbar = Panel(scale=5, model='quad')
healthbar.alpha = 0

print("player initiated")

gun = Entity(model='cube', parent=camera, position=(.5, -.25, .25), scale=(.3, .2, 1), origin_z=-.5, color=color.red,
             on_cooldown=False)
gun.muzzle_flash = Entity(parent=gun, z=1, world_scale=.5, model='quad', color=color.yellow, enabled=False)

grappleGun = Entity(model='cube', parent=camera, position=(-.5, -.25, .25), scale=(.3, .2, 1), origin_z=-.5,
                    color=color.green, grappling = False)
grappleGun.flash = Entity(parent=grappleGun, z=1, world_scale=.5, model='quad', color=color.blue, enabled=False)

print("weapons loaded")

# ======================================================= SETUP ======================================================================
ui = UI(editor_camera, player, gun, grappleGun, resetEnemies)
worldSetup()



#   ======================================================= GAME FUNCS ======================================================================
def update():
    player.immuneTimer -= time.dt
    if player.hp <= 0:
        ui.on_player_death()

    if held_keys['left mouse']:
        shoot()

    if held_keys['right mouse']:
        grapple()
    elif not held_keys['right mouse'] and grappleGun.grappling:
        release_grapple()



def grapple():
    # only detect point of impact if not already grappling
    if not grappleGun.grappling:  
        
        # grapple properties
        direction = camera.forward
        maxGrappleDistance = 50

        # detect the point of impact
        hitData = raycast(grappleGun.flash.world_position, direction, maxGrappleDistance, ignore=[player])

        # start grappling animation
        if hitData.hit:
            grappleGun.flash.enabled = True
            grappleGun.grappling = True
            print("grapple start")
            
    # player is already grappling, update their position towards the point of impact
    else:  
        print("grapple in progress")
        # ADD: pullIncr.pull incrememnt is a portion of pull line. 
        # use to update player position while grappling 
        # ADD: pullProgress. progress of player along the line.
        # use to track progress of player grappling towards trajectory

        # pull Line is the 3d vector towards the hit point  
        # pullLine = hitData.world_point - player.position
        # while grappleGun.grappling and pullLine.length() > 0:
        #     player.position += pullLine.normalized() * pullSpeed * time.dt
        #     pullLine = hitData.world_point - player.position


def release_grapple():
    if grappleGun.grappling:
        grappleGun.grappling = False
        grappleGun.flash.enabled = False
        print("grapple released")


def shoot():
    if not gun.on_cooldown:
        # print('shoot')
        gun.on_cooldown = True
        gun.muzzle_flash.enabled = True
        from ursina.prefabs.ursfx import ursfx
        ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise',
              pitch=random.uniform(-13, -12), pitch_change=-12, speed=3.0)
        invoke(gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.15)
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 100
            mouse.hovered_entity.blink(color.red)



app.run()
