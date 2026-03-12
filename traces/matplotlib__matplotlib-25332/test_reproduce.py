import matplotlib.pyplot as plt
import pickle

def test_align_labels_pickle():
    """
    Test that a figure can be pickled after calling align_labels().

    This test reproduces the issue where calling align_labels() on a figure
    makes it unpicklable due to weakref.ReferenceType objects.
    """
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    time = [0, 1, 2, 3, 4]
    speed = [40000, 4300, 4500, 4700, 4800]
    acc = [10, 11, 12, 13, 14]
    ax1.plot(time, speed)
    ax1.set_ylabel('speed')
    ax2.plot(time, acc)
    ax2.set_ylabel('acc')

    # This is the critical line that causes the issue
    fig.align_labels()

    # Try to pickle the figure - this should fail on base commit
    try:
        pickled_data = pickle.dumps(fig)
        # If we get here, pickling succeeded
        print("SUCCESS: Figure was pickled successfully")
        # Try to unpickle to make sure it works completely
        unpickled_fig = pickle.loads(pickled_data)
        print("SUCCESS: Figure was unpickled successfully")
        plt.close(unpickled_fig)
        plt.close(fig)
        return True
    except TypeError as e:
        print(f"FAILED: {e}")
        plt.close(fig)
        return False

if __name__ == "__main__":
    success = test_align_labels_pickle()
    if success:
        print("Test passed - issue is fixed")
    else:
        print("Test failed - issue reproduced")
        exit(1)