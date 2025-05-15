import os
import logging
import random
from flask import Flask, render_template, request, session, redirect, url_for, jsonify

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "pipeline-panic-key-fixed")

# Game configuration
PIPELINE_STAGES = ["Code", "Build", "Test", "Deploy"]
MAX_TURNS = 5
MAX_WRONG_CHOICES = 3

# Game obstacles and correct choices
OBSTACLES = {
    "Code": [
        {
            "obstacle": "Your repository has conflicts after a merge.",
            "choices": [
                {"text": "Force push your changes", "correct": False},
                {"text": "Resolve conflicts and commit", "correct": True},
                {"text": "Create a new branch", "correct": False}
            ]
        },
        {
            "obstacle": "Code isn't following style guidelines.",
            "choices": [
                {"text": "Ignore style issues", "correct": False},
                {"text": "Run linter and fix errors", "correct": True},
                {"text": "Disable style checking", "correct": False}
            ]
        }
    ],
    "Build": [
        {
            "obstacle": "Build is failing due to missing dependencies.",
            "choices": [
                {"text": "Skip the build step", "correct": False},
                {"text": "Add dependencies to requirements", "correct": True},
                {"text": "Build on a different server", "correct": False}
            ]
        },
        {
            "obstacle": "Build agent is offline.",
            "choices": [
                {"text": "Wait until tomorrow", "correct": False},
                {"text": "Restart build agent", "correct": True},
                {"text": "Deploy without building", "correct": False}
            ]
        }
    ],
    "Test": [
        {
            "obstacle": "Unit tests are failing.",
            "choices": [
                {"text": "Skip failing tests", "correct": False},
                {"text": "Fix the failing tests", "correct": True},
                {"text": "Deploy anyway", "correct": False}
            ]
        },
        {
            "obstacle": "Integration tests are timing out.",
            "choices": [
                {"text": "Increase timeout threshold", "correct": False},
                {"text": "Optimize test performance", "correct": True},
                {"text": "Skip integration tests", "correct": False}
            ]
        }
    ],
    "Deploy": [
        {
            "obstacle": "Deployment target is out of disk space.",
            "choices": [
                {"text": "Force the deployment", "correct": False},
                {"text": "Clean up old deployments", "correct": True},
                {"text": "Deploy to a different environment", "correct": False}
            ]
        },
        {
            "obstacle": "Production database needs migration.",
            "choices": [
                {"text": "Skip database migration", "correct": False},
                {"text": "Run migration with deployment", "correct": True},
                {"text": "Roll back the deployment", "correct": False}
            ]
        }
    ]
}

# Icons for each stage
STAGE_ICONS = {
    "Code": "💻",
    "Build": "⚙️",
    "Test": "🧪",
    "Deploy": "🚀"
}

@app.route('/')
def index():
    """Render the home page with game instructions."""
    return render_template('index.html')

@app.route('/game')
def game():
    """Initialize and render the game page."""
    # Check if we need to reset the game
    if 'current_stage' not in session:
        logging.debug("Creating new game...")
        # Reset game state
        session['stage_index'] = 0
        session['current_stage'] = PIPELINE_STAGES[0]
        session['turns'] = 0
        session['wrong_choices'] = 0
        session['score'] = 0
        session['stages_completed'] = []
        
        # Select random obstacle for the first stage
        current_stage = PIPELINE_STAGES[0]
        obstacle = random.choice(OBSTACLES[current_stage])
        session['current_obstacle'] = obstacle
    
    # Get the current game state
    current_stage = session.get('current_stage')
    obstacle = session.get('current_obstacle')
    stage_index = session.get('stage_index', 0)
    turns = session.get('turns', 0)
    wrong_choices = session.get('wrong_choices', 0)
    score = session.get('score', 0)
    stages_completed = session.get('stages_completed', [])
    
    # Debug: log the current game state
    logging.debug(f"Rendering game with stage: {current_stage}, obstacle: {obstacle}")
    
    return render_template('game.html', 
                          stage=current_stage,
                          stage_index=stage_index,
                          stages=PIPELINE_STAGES,
                          stage_icons=STAGE_ICONS,
                          obstacle=obstacle,
                          turns=turns,
                          wrong_choices=wrong_choices,
                          score=score,
                          stages_completed=stages_completed)

@app.route('/make_choice', methods=['POST'])
def make_choice():
    """Process player choice and update game state."""
    if request.method != 'POST':
        return redirect(url_for('game'))
    
    # Debug: log the request and session
    logging.debug(f"make_choice called with method: {request.method}")
    logging.debug(f"Session before choice: {dict(session)}")
    
    try:
        choice_index = int(request.form.get('choice', 0))
        logging.debug(f"Choice index selected: {choice_index}")
    except ValueError:
        logging.error(f"Invalid choice value: {request.form.get('choice')}")
        return redirect(url_for('game'))
    
    # Make sure we have a game in progress
    if 'current_stage' not in session or 'current_obstacle' not in session:
        logging.warning("No game in progress, redirecting to new game")
        return redirect(url_for('game'))
    
    # Get current stage and obstacle from session
    current_stage = session['current_stage']
    obstacle = session['current_obstacle']
    
    # Check if choice is correct
    choices = obstacle.get('choices', [])
    if not choices or choice_index >= len(choices):
        logging.warning(f"Invalid choice index {choice_index} for choices length {len(choices) if choices else 0}")
        return redirect(url_for('game'))
        
    choice = choices[choice_index]
    is_correct = choice.get('correct', False)
    logging.debug(f"Choice is correct: {is_correct}")
    
    # Update turns count
    session['turns'] = session.get('turns', 0) + 1
    
    # Update score and wrong choices based on player's choice
    if is_correct:
        session['score'] = session.get('score', 0) + 10
        
        # Add current stage to completed stages if not already there
        completed_stages = session.get('stages_completed', [])
        if current_stage not in completed_stages:
            completed_stages.append(current_stage)
        session['stages_completed'] = completed_stages
        
        # Advance to next stage
        stage_index = session.get('stage_index', 0) + 1
        session['stage_index'] = stage_index
        
        # Check if all stages are completed
        if stage_index >= len(PIPELINE_STAGES):
            logging.debug("All stages completed, redirecting to success end screen")
            return redirect(url_for('end', result='success'))
        
        # Set up next stage
        next_stage = PIPELINE_STAGES[stage_index]
        session['current_stage'] = next_stage
        session['current_obstacle'] = random.choice(OBSTACLES[next_stage])
        logging.debug(f"Advanced to next stage: {next_stage}")
    else:
        session['score'] = max(0, session.get('score', 0) - 5)  # Don't go below 0
        session['wrong_choices'] = session.get('wrong_choices', 0) + 1
        
        # Select a new obstacle for the current stage
        if current_stage in OBSTACLES:
            session['current_obstacle'] = random.choice(OBSTACLES[current_stage])
        logging.debug(f"Wrong choice, wrong_choices now: {session.get('wrong_choices')}")
    
    # Check if game should end
    if session.get('turns', 0) >= MAX_TURNS:
        logging.debug("Max turns reached, redirecting to timeout end screen")
        return redirect(url_for('end', result='timeout'))
    
    if session.get('wrong_choices', 0) >= MAX_WRONG_CHOICES:
        logging.debug("Max wrong choices reached, redirecting to failed end screen")
        return redirect(url_for('end', result='failed'))
    
    logging.debug(f"Session after choice: {dict(session)}")
    
    return redirect(url_for('game'))

@app.route('/game_state')
def game_state():
    """Return the current game state as JSON."""
    # Debug: log the session
    logging.debug(f"game_state called, session: {dict(session)}")
    
    # If no game in progress, return empty state
    if 'current_stage' not in session:
        logging.warning("No game in progress for game_state request")
        return jsonify({
            'stage': None,
            'stage_index': 0,
            'turns': 0,
            'wrong_choices': 0,
            'score': 0,
            'stages_completed': []
        })
    
    return jsonify({
        'stage': session.get('current_stage'),
        'stage_index': session.get('stage_index', 0),
        'turns': session.get('turns', 0),
        'wrong_choices': session.get('wrong_choices', 0),
        'score': session.get('score', 0),
        'stages_completed': session.get('stages_completed', [])
    })

@app.route('/end')
def end():
    """Render the end game screen with results."""
    # Get result from request args
    result = request.args.get('result', 'unknown')
    
    # Get game state from session
    score = session.get('score', 0)
    turns = session.get('turns', 0)
    wrong_choices = session.get('wrong_choices', 0)
    
    # Debug log the end game state
    logging.debug(f"Ending game with result: {result}, score: {score}, turns: {turns}")
    
    # Determine end message based on result
    if result == 'success':
        message = "Congratulations! Your CI/CD pipeline is successfully deployed!"
    elif result == 'timeout':
        message = "You ran out of turns. The release deadline was missed."
    elif result == 'failed':
        message = "Too many wrong choices. The pipeline has failed."
    else:
        message = "Game over. Better luck next time!"
    
    # Clear the session for the next game
    session.clear()
    
    return render_template('end.html', 
                          result=result, 
                          message=message,
                          score=score,
                          turns=turns,
                          wrong_choices=wrong_choices)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
