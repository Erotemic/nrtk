import numpy as np
import pytest
from contextlib import nullcontext as does_not_raise
from smqtk_core.configuration import configuration_test_helper
from typing import Any, ContextManager, Dict, Type, Union

from nrtk.impls.perturb_image.skimage.random_noise import (
    GaussianNoisePerturber,
    PepperNoisePerturber,
    SaltAndPepperNoisePerturber,
    SaltNoisePerturber,
    SpeckleNoisePerturber,
    _SKImageNoisePerturber
)

from ..test_perturber_utils import perturber_assertions


def rng_assertions(perturber: Type[_SKImageNoisePerturber], rng: int) -> None:
    """
    Test that output is reproducible if a rng or seed is provided.

    :param perturber: SKImage random_noise perturber class of interest.
    :param rng: Seed value.
    """
    dummy_image_A = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
    dummy_image_B = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)

    # Test as seed value
    inst1 = perturber(rng=rng)
    out1A = inst1(dummy_image_A)
    out1B = inst1(dummy_image_B)
    inst2 = perturber(rng=rng)
    out2A = inst2(dummy_image_A)
    out2B = inst2(dummy_image_B)
    assert np.array_equal(out1A, out2A)
    assert np.array_equal(out1B, out2B)

    # Test generator
    inst3 = perturber(rng=np.random.default_rng(rng))
    out3A = inst3(dummy_image_A)
    out3B = inst3(dummy_image_B)
    inst4 = perturber(rng=np.random.default_rng(rng))
    out4A = inst4(dummy_image_A)
    out4B = inst4(dummy_image_B)
    assert np.array_equal(out3A, out4A)
    assert np.array_equal(out3B, out4B)


class TestSaltNoisePerturber:
    def test_consistency(self) -> None:
        """
        Run on a dummy image to ensure output matches precomputed results.
        """
        image = np.zeros((3, 3), dtype=np.uint8)
        rng = 42
        amount = 0.5

        # Test perturb interface directly
        inst = SaltNoisePerturber(amount=amount, rng=rng)
        perturber_assertions(perturb=inst.perturb, image=image, expected=EXPECTED_SALT)

        # Test callable
        perturber_assertions(
            perturb=SaltNoisePerturber(amount=amount, rng=rng),
            image=image,
            expected=EXPECTED_SALT
        )

    @pytest.mark.parametrize("image, expectation", [
        (np.zeros((256, 256, 3), dtype=np.uint8), does_not_raise()),
        (np.ones((256, 256, 3), dtype=np.uint8) * 255, does_not_raise()),
        (np.zeros((256, 256, 3), dtype=np.float32), does_not_raise()),
        (np.ones((256, 256, 3), dtype=np.float32), does_not_raise()),
        (np.ones((256, 256, 3), dtype=np.half), does_not_raise()),
        (np.ones((256, 356, 3), dtype=np.csingle),
            pytest.raises(NotImplementedError, match=r"Perturb not implemented for"))
    ])
    def test_no_perturbation(self, image: np.ndarray, expectation: ContextManager) -> None:
        """
        Run a dummy image through the perturber with settings for no
        perturbations, expect to get same image back (quantization errors
        possible). This attempts to isolate perturber implementation code
        from external calls to the extent that is possible.
        """
        with expectation:
            perturber_assertions(perturb=SaltNoisePerturber(amount=0), image=image, expected=image)

    @pytest.mark.parametrize("rng", [42, 12345])
    def test_rng(self, rng: int) -> None:
        """
        Ensure results are reproducible.
        """
        rng_assertions(perturber=SaltNoisePerturber, rng=rng)

    @pytest.mark.parametrize("rng, amount", [
        (42, 0.8),
        (np.random.default_rng(12345), 0.3)
    ])
    def test_configuration(self, rng: Union[np.random.Generator, int], amount: float) -> None:
        """
        Test configuration stability.
        """
        inst = SaltNoisePerturber(rng=rng, amount=amount)
        for i in configuration_test_helper(inst):
            assert i.rng == rng
            assert i.amount == amount

    @pytest.mark.parametrize("kwargs, expectation", [
        ({"amount": 0.5}, does_not_raise()),
        ({"amount": 0}, does_not_raise()),
        ({"amount": 1}, does_not_raise()),
        ({"amount": 2.}, pytest.raises(ValueError, match=r"SaltNoisePerturber invalid amount")),
        ({"amount": -3.}, pytest.raises(ValueError, match=r"SaltNoisePerturber invalid amount"))
    ])
    def test_configuration_bounds(self, kwargs: Dict[str, Any], expectation: ContextManager) -> None:
        """
        Test that an exception is properly raised (or not) based on argument value.
        """
        with expectation:
            SaltNoisePerturber(**kwargs)


class TestPepperNoisePerturber:
    def test_consistency(self) -> None:
        """
        Run on a dummy image to ensure output matches precomputed results.
        """
        image = np.ones((3, 3), dtype=np.uint8) * 255
        rng = 42
        amount = 0.5

        # Test perturb interface directly
        inst = PepperNoisePerturber(amount=amount, rng=rng)
        perturber_assertions(perturb=inst.perturb, image=image, expected=EXPECTED_PEPPER)

        # Test callable
        perturber_assertions(
            perturb=PepperNoisePerturber(amount=amount, rng=rng),
            image=image,
            expected=EXPECTED_PEPPER
        )

    @pytest.mark.parametrize("image, expectation", [
        (np.zeros((256, 256, 3), dtype=np.uint8), does_not_raise()),
        (np.ones((256, 256, 3), dtype=np.uint8) * 255, does_not_raise()),
        (np.zeros((256, 256, 3), dtype=np.float32), does_not_raise()),
        (np.ones((256, 256, 3), dtype=np.float32), does_not_raise()),
        (np.ones((256, 256, 3), dtype=np.half), does_not_raise()),
        (np.ones((256, 356, 3), dtype=np.csingle),
            pytest.raises(NotImplementedError, match=r"Perturb not implemented for"))
    ])
    def test_no_perturbation(self, image: np.ndarray, expectation: ContextManager) -> None:
        """
        Run a dummy image through the perturber with settings for no
        perturbations, expect to get same image back (quantization errors
        possible). This attempts to isolate perturber implementation code
        from external calls to the extent that is possible.
        """
        with expectation:
            perturber_assertions(perturb=PepperNoisePerturber(amount=0), image=image, expected=image)

    @pytest.mark.parametrize("rng", [42, 12345])
    def test_rng(self, rng: int) -> None:
        """
        Ensure results are reproducible.
        """
        rng_assertions(perturber=PepperNoisePerturber, rng=rng)

    @pytest.mark.parametrize("rng, amount", [
        (42, 0.8),
        (np.random.default_rng(12345), 0.3)
    ])
    def test_configuration(self, rng: Union[np.random.Generator, int], amount: float) -> None:
        """
        Test configuration stability.
        """
        inst = PepperNoisePerturber(rng=rng, amount=amount)
        for i in configuration_test_helper(inst):
            assert i.rng == rng
            assert i.amount == amount

    @pytest.mark.parametrize("kwargs, expectation", [
        ({"amount": 0.25}, does_not_raise()),
        ({"amount": 0}, does_not_raise()),
        ({"amount": 1}, does_not_raise()),
        ({"amount": 2.5}, pytest.raises(ValueError, match=r"PepperNoisePerturber invalid amount")),
        ({"amount": -4.2}, pytest.raises(ValueError, match=r"PepperNoisePerturber invalid amount"))
    ])
    def test_configuration_bounds(self, kwargs: Dict[str, Any], expectation: ContextManager) -> None:
        """
        Test that an exception is properly raised (or not) based on argument value.
        """
        with expectation:
            PepperNoisePerturber(**kwargs)


class TestSaltAndPepperNoisePerturber:
    def test_consistency(self) -> None:
        """
        Run on a dummy image to ensure output matches precomputed results.
        """
        image = np.zeros((3, 3), dtype=np.uint8)
        rng = 42
        amount = 0.5
        salt_vs_pepper = 0.5

        # Test perturb interface directly
        inst = SaltAndPepperNoisePerturber(amount=amount, salt_vs_pepper=salt_vs_pepper, rng=rng)
        perturber_assertions(perturb=inst.perturb, image=image, expected=EXPECTED_SP)

        # Test callable
        perturber_assertions(
            perturb=SaltAndPepperNoisePerturber(amount=amount, salt_vs_pepper=salt_vs_pepper, rng=rng),
            image=image,
            expected=EXPECTED_SP
        )

    @pytest.mark.parametrize("image, expectation", [
        (np.zeros((256, 256, 3), dtype=np.uint8), does_not_raise()),
        (np.ones((256, 256, 3), dtype=np.uint8) * 255, does_not_raise()),
        (np.zeros((256, 256, 3), dtype=np.float32), does_not_raise()),
        (np.ones((256, 256, 3), dtype=np.float32), does_not_raise()),
        (np.ones((256, 256, 3), dtype=np.half), does_not_raise()),
        (np.ones((256, 356, 3), dtype=np.csingle),
            pytest.raises(NotImplementedError, match=r"Perturb not implemented for"))
    ])
    def test_no_perturbation(self, image: np.ndarray, expectation: ContextManager) -> None:
        """
        Run a dummy image through the perturber with settings for no
        perturbations, expect to get same image back (quantization errors
        possible). This attempts to isolate perturber implementation code
        from external calls to the extent that is possible.
        """
        with expectation:
            perturber_assertions(perturb=SaltAndPepperNoisePerturber(amount=0), image=image, expected=image)

    @pytest.mark.parametrize("rng", [42, 12345])
    def test_rng(self, rng: int) -> None:
        """
        Ensure results are reproducible.
        """
        rng_assertions(perturber=SaltAndPepperNoisePerturber, rng=rng)

    @pytest.mark.parametrize("rng, amount, salt_vs_pepper", [
        (42, 0.8, 0.25),
        (np.random.default_rng(12345), 0.3, 0.2)
    ])
    def test_configuration(self, rng: Union[np.random.Generator, int], amount: float, salt_vs_pepper: float) -> None:
        """
        Test configuration stability.
        """
        inst = SaltAndPepperNoisePerturber(rng=rng, amount=amount, salt_vs_pepper=salt_vs_pepper)
        for i in configuration_test_helper(inst):
            assert i.rng == rng
            assert i.amount == amount
            assert i.salt_vs_pepper == salt_vs_pepper

    @pytest.mark.parametrize("kwargs, expectation", [
        ({"amount": 0.45}, does_not_raise()),
        ({"amount": 0}, does_not_raise()),
        ({"amount": 1}, does_not_raise()),
        ({"amount": 1.2}, pytest.raises(ValueError, match=r"SaltAndPepperNoisePerturber invalid amount")),
        ({"amount": -0.2}, pytest.raises(ValueError, match=r"SaltAndPepperNoisePerturber invalid amount")),
        ({"salt_vs_pepper": 0.2}, does_not_raise()),
        ({"salt_vs_pepper": 0}, does_not_raise()),
        ({"salt_vs_pepper": 1}, does_not_raise()),
        ({"salt_vs_pepper": 5}, pytest.raises(ValueError, match=r"SaltAndPepperNoisePerturber invalid salt_vs_pepper")),
        ({"salt_vs_pepper": -3}, pytest.raises(ValueError, match=r"SaltAndPepperNoisePerturber invalid salt_vs_pepper"))
    ])
    def test_configuration_bounds(self, kwargs: Dict[str, Any], expectation: ContextManager) -> None:
        """
        Test that an exception is properly raised (or not) based on argument value.
        """
        with expectation:
            SaltAndPepperNoisePerturber(**kwargs)


class TestGaussianNoisePerturber:
    def test_consistency(self) -> None:
        """
        Run on a dummy image to ensure output matches precomputed results.
        """
        image = np.zeros((3, 3), dtype=np.uint8)
        rng = 42
        mean = 0
        var = 0.05

        # Test perturb interface directly
        inst = GaussianNoisePerturber(mean=mean, var=var, rng=rng)
        perturber_assertions(perturb=inst.perturb, image=image, expected=EXPECTED_GAUSSIAN)

        # Test callable
        perturber_assertions(
            perturb=GaussianNoisePerturber(mean=mean, var=var, rng=rng),
            image=image,
            expected=EXPECTED_GAUSSIAN
        )

    @pytest.mark.parametrize("image, expectation", [
        (np.zeros((256, 256, 3), dtype=np.uint8), does_not_raise()),
        (np.ones((256, 256, 3), dtype=np.uint8) * 255, does_not_raise()),
        (np.zeros((256, 256, 3), dtype=np.float32), does_not_raise()),
        (np.ones((256, 256, 3), dtype=np.float32), does_not_raise()),
        (np.ones((256, 256, 3), dtype=np.half), does_not_raise()),
        (np.ones((256, 356, 3), dtype=np.csingle),
            pytest.raises(NotImplementedError, match=r"Perturb not implemented for"))
    ])
    def test_no_perturbation(self, image: np.ndarray, expectation: ContextManager) -> None:
        """
        Run a dummy image through the perturber with settings for no
        perturbations, expect to get same image back (quantization errors
        possible). This attempts to isolate perturber implementation code
        from external calls to the extent that is possible.
        """
        with expectation:
            perturber_assertions(perturb=GaussianNoisePerturber(mean=0, var=0), image=image, expected=image)

    @pytest.mark.parametrize("rng", [42, 12345])
    def test_rng(self, rng: int) -> None:
        """
        Ensure results are reproducible.
        """
        rng_assertions(perturber=GaussianNoisePerturber, rng=rng)

    @pytest.mark.parametrize("rng, mean, var", [
        (42, 0.8, 0.25),
        (np.random.default_rng(12345), 0.3, 0.2)
    ])
    def test_configuration(self, rng: Union[np.random.Generator, int], mean: float, var: float) -> None:
        """
        Test configuration stability.
        """
        inst = GaussianNoisePerturber(rng=rng, mean=mean, var=var)
        for i in configuration_test_helper(inst):
            assert i.rng == rng
            assert i.mean == mean
            assert i.var == var

    @pytest.mark.parametrize("kwargs, expectation", [
        ({"var": 0.75}, does_not_raise()),
        ({"var": 0}, does_not_raise()),
        ({"var": -10}, pytest.raises(ValueError, match=r"GaussianNoisePerturber invalid var"))
    ])
    def test_configuration_bounds(self, kwargs: Dict[str, Any], expectation: ContextManager) -> None:
        """
        Test that an exception is properly raised (or not) based on argument value.
        """
        with expectation:
            GaussianNoisePerturber(**kwargs)


class TestSpeckleNoisePerturber:
    def test_consistency(self) -> None:
        """
        Run on a dummy image to ensure output matches precomputed results.
        """
        image = np.ones((3, 3), dtype=np.uint8) * 255
        rng = 42
        mean = 0
        var = 0.05

        # Test perturb interface directly
        inst = SpeckleNoisePerturber(mean=mean, var=var, rng=rng)
        perturber_assertions(perturb=inst.perturb, image=image, expected=EXPECTED_SPECKLE)

        # Test callable
        perturber_assertions(
            perturb=SpeckleNoisePerturber(mean=mean, var=var, rng=rng),
            image=image,
            expected=EXPECTED_SPECKLE
        )

    @pytest.mark.parametrize("image, expectation", [
        (np.zeros((256, 256, 3), dtype=np.uint8), does_not_raise()),
        (np.ones((256, 256, 3), dtype=np.uint8) * 255, does_not_raise()),
        (np.zeros((256, 256, 3), dtype=np.float32), does_not_raise()),
        (np.ones((256, 256, 3), dtype=np.float32), does_not_raise()),
        (np.ones((256, 256, 3), dtype=np.half), does_not_raise()),
        (np.ones((256, 356, 3), dtype=np.csingle),
            pytest.raises(NotImplementedError, match=r"Perturb not implemented for"))
    ])
    def test_no_perturbation(self, image: np.ndarray, expectation: ContextManager) -> None:
        """
        Run a dummy image through the perturber with settings for no
        perturbations, expect to get same image back (quantization errors
        possible). This attempts to isolate perturber implementation code
        from external calls to the extent that is possible.
        """
        with expectation:
            perturber_assertions(perturb=SpeckleNoisePerturber(mean=0, var=0), image=image, expected=image)

    @pytest.mark.parametrize("rng", [42, 12345])
    def test_rng(self, rng: int) -> None:
        """
        Ensure results are reproducible.
        """
        rng_assertions(perturber=SpeckleNoisePerturber, rng=rng)

    @pytest.mark.parametrize("rng, mean, var", [
        (42, 0.8, 0.25),
        (np.random.default_rng(12345), 0.3, 0.2)
    ])
    def test_configuration(self, rng: Union[np.random.Generator, int], mean: float, var: float) -> None:
        """
        Test configuration stability.
        """
        inst = SpeckleNoisePerturber(rng=rng, mean=mean, var=var)
        for i in configuration_test_helper(inst):
            assert i.rng == rng
            assert i.mean == mean
            assert i.var == var

    @pytest.mark.parametrize("kwargs, expectation", [
        ({"var": 0.123}, does_not_raise()),
        ({"var": 0}, does_not_raise()),
        ({"var": -10}, pytest.raises(ValueError, match=r"SpeckleNoisePerturber invalid var"))
    ])
    def test_configuration_bounds(self, kwargs: Dict[str, Any], expectation: ContextManager) -> None:
        """
        Test that an exception is properly raised (or not) based on argument value.
        """
        with expectation:
            SpeckleNoisePerturber(**kwargs)


EXPECTED_SALT = np.array([[0, 255, 0], [0, 255, 0], [0, 0, 255]], dtype=np.uint8)
EXPECTED_PEPPER = np.array([[255, 0, 255], [255, 0, 255], [255, 255, 0]], dtype=np.uint8)
EXPECTED_SP = np.array([[0, 255, 0], [0, 0, 0], [0, 0, 255]], dtype=np.uint8)
EXPECTED_GAUSSIAN = np.array([[17, 0, 43], [54, 0, 0], [7, 0, 0]], dtype=np.uint8)
EXPECTED_SPECKLE = np.array([[255, 196, 255], [255, 144, 181], [255, 237, 254]], dtype=np.uint8)
