def getRoleDescription(role):
    townsFolk = ' is a member of the Townsfolk, and wins the game by ensuring no Mafia member is still alive.\n'
    mafia = ' is a member of the Mafia, and wins the game if all the Townsfolk are killed.\n'
    if role == 'Doctor': return 'The Doctor' + townsFolk + 'The Doctor can select one Player to heal every night (including yourself). This will prevent that Player from dying if they are attacked.\nYou cannot heal the same person twice in a row, however.'
    if role == 'Framer': return 'The Framer' + mafia + 'The Framer can select one Player to frame every night. This will make the target appear suspicious if investigated by an Investigator.\n If the Murderer dies, YOU will replace them and become the next Murderer.'
    if role == 'Murderer': return 'The Murderer' + mafia + 'The Murderer can select one Player to murder every night.\n'
    if role == 'Escort': return 'The Escort' + townsFolk + 'The Escort can select one Player to escort every night, preventing that Player from being able to perform their role.\nYou cannot escort the same person twice in a row, however.'
    if role == 'Detective': return 'The Detective' + townsFolk + 'The Detective can select one Player to investigate every night, and will receive the results of the investigation the next night.\nThe Detective searches for blood, which will appear on the Murderer, Doctor, or anybody that was framed'
    if role == 'Medium': return 'The Medium' + townsFolk + 'The Medium can speak to the dead at night'
    if role == 'Towny': return 'The Towny' + townsFolk + 'They do not have any special roles.'
    if role == 'Jailor': return 'The Jailor' + townsFolk
    if role == 'Executioner': return 'The Executioner wins the game by getting their target lynched. If their target is killed by another means, the Executioner will become a Jester'
    if role == 'Jester': return 'The Jester wins the game by getting lynched, simple as that'
    if role == 'Mayor': return 'The Mayor' + townsFolk + 'The Mayor can reveal his role to the group before a round of voting begins. His vote will be worth 3 points from then on'
    if role == 'Serial Killer': return 'The Serial Killer wins the game by being the last person alive. They can achieve this by killing. And lots of it!'
    return 'oops no role Description, program brokey'
        
def getActionDescription(role):
    if role == 'Doctor': return 'Who would you like to heal?  (or leave blank to abstain)'
    if role == 'Framer': return 'Who would you like to frame?  (or leave blank to abstain)'
    if role == 'Murderer': return 'Who would you like to murder?  (or leave blank to abstain)'
    if role == 'Escort': return 'Who would you like to escort?  (or leave blank to abstain)'
    if role == 'Detective':  return 'Who would you like to investigate?  (or leave blank to abstain)'
    if role == 'Jailor': return 'Who would you like to jail?  (or leave blank to abstain)'
    if role == 'Serial Killer': return 'Who would you like to kill?  (or leave blank to abstain)'
    return 'oops no action Description, program brokey'
        