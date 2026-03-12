import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import pickle
import sys

def test_pickle_draggable_legend():
    """
    Test that a figure with a draggable legend can be pickled.

    This test reproduces the issue where pickling a figure with a draggable legend
    raises a TypeError about not being able to pickle canvas objects.

    The test should:
    - FAIL on base commit (430fb1db88) with TypeError or AttributeError
    - PASS on head commit (0849036fd9) after the fix
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)

    time = [0, 1, 2, 3, 4]
    speed = [40, 43, 45, 47, 48]

    ax.plot(time, speed, label="speed")

    leg = ax.legend()
    leg.set_draggable(True)  # This is what causes the pickling issue

    # Check if the draggable object has canvas as an attribute vs property
    draggable = leg._draggable
    has_canvas_attr = hasattr(draggable, 'canvas')

    print(f"Draggable object has 'canvas' attribute: {has_canvas_attr}")

    # Check if canvas is an attribute or property
    if has_canvas_attr:
        # Try to check if it's a property by looking at the class
        is_property = isinstance(getattr(type(draggable), 'canvas', None), property)
        print(f"canvas is a property: {is_property}")

        if not is_property:
            print("ERROR: canvas is an attribute, not a property - this will cause pickling issues!")
            return False

    try:
        # Try to pickle the figure
        pickled_data = pickle.dumps(fig)
        print("SUCCESS: Figure with draggable legend was pickled successfully")

        # Also try to unpickle to make sure it works
        unpickled_fig = pickle.loads(pickled_data)
        print("SUCCESS: Figure was unpickled successfully")

        return True
    except (TypeError, AttributeError) as e:
        print(f"FAILURE: Could not pickle figure with draggable legend: {e}")
        return False

if __name__ == "__main__":
    success = test_pickle_draggable_legend()
    if not success:
        print("\nTest FAILED - issue reproduced (expected on base commit)")
        sys.exit(1)
    else:
        print("\nTest PASSED - issue is fixed (expected on head commit)")
        sys.exit(0)